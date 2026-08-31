"""
MedBill Enterprise - Doctor Consultation Tariff Calculator
Calculates consultation fees across OPD, IPD, Emergency Triage, and Telemedicine encounters.
Includes rank multipliers, night/weekend surcharges, follow-up window validity rules,
and generates structured billing line items.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid

from medbill.core.models import (
    Doctor,
    DoctorRank,
    Encounter,
    EncounterType,
    TriageLevel,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.catalogs.doctors_specialties import (
    SPECIALTY_CATALOG,
    SpecialtyTariffSchedule,
    get_specialty_schedule,
)


class ConsultationTariffCalculator:
    """
    Enterprise calculator for clinical consultation tariffs.
    Handles OPD, IPD ward visits, Emergency triage escalations, and Telemedicine encounters.
    """

    # Triage multiplier for emergency presentations
    TRIAGE_MULTIPLIERS: Dict[TriageLevel, float] = {
        TriageLevel.LEVEL_1_RESUSCITATION: 2.50,
        TriageLevel.LEVEL_2_EMERGENT: 2.00,
        TriageLevel.LEVEL_3_URGENT: 1.50,
        TriageLevel.LEVEL_4_SEMI_URGENT: 1.20,
        TriageLevel.LEVEL_5_NON_URGENT: 1.00,
    }

    # Night hours surcharge (20:00 to 07:00)
    NIGHT_SURCHARGE_PERCENT = 30.0  # +30%
    # Weekend surcharge (Saturday & Sunday)
    WEEKEND_SURCHARGE_PERCENT = 20.0  # +20%

    def __init__(self, specialty_catalog: Optional[Dict[str, SpecialtyTariffSchedule]] = None):
        self.specialty_catalog = specialty_catalog or SPECIALTY_CATALOG

    def is_night_time(self, visit_time: datetime) -> bool:
        """Check if consultation occurred during night on-call hours (8 PM - 7 AM)."""
        hour = visit_time.hour
        return hour >= 20 or hour < 7

    def is_weekend(self, visit_time: datetime) -> bool:
        """Check if consultation occurred on a weekend (Saturday or Sunday)."""
        return visit_time.weekday() in (5, 6)

    def is_within_followup_window(
        self,
        doctor: Doctor,
        current_visit_time: datetime,
        previous_visit_time: Optional[datetime] = None
    ) -> bool:
        """
        Determines if current visit is within the doctor's specialty follow-up window.
        If previous_visit_time is within validity days, this returns True.
        """
        if not previous_visit_time:
            return False

        sched = self.specialty_catalog.get(doctor.specialty_code)
        validity_days = sched.follow_up_validity_days if sched else 7
        delta = current_visit_time - previous_visit_time
        return 0 <= delta.days <= validity_days

    def calculate_consultation_charge(
        self,
        doctor: Doctor,
        encounter: Encounter,
        visit_time: Optional[datetime] = None,
        previous_visit_time: Optional[datetime] = None,
        is_emergency: bool = False,
        is_telemedicine: bool = False,
        cpt_code: Optional[str] = None
    ) -> BillingLineItem:
        """
        Main calculation engine for consultation billing line item.
        """
        actual_time = visit_time or encounter.admission_time or datetime.utcnow()
        sched = self.specialty_catalog.get(doctor.specialty_code)

        # 1. Base Tariff determination
        if is_telemedicine or encounter.encounter_type == EncounterType.TELEMEDICINE:
            base_fee = doctor.telemedicine_fee or (sched.telemedicine_fee if sched else 70.00)
            description_prefix = "Telemedicine Consultation"
            default_cpt = "99213"
        elif is_emergency or encounter.encounter_type == EncounterType.EMERGENCY:
            base_fee = sched.emergency_oncall_fee if sched else 200.00
            description_prefix = "Emergency Consultation"
            default_cpt = "99284"
        elif encounter.encounter_type == EncounterType.INPATIENT:
            base_fee = sched.base_ipd_visit_fee if sched else 100.00
            description_prefix = "Inpatient Daily Visit"
            default_cpt = "99232"
        else:
            base_fee = doctor.base_consultation_fee or (sched.base_opd_fee if sched else 85.00)
            description_prefix = "Outpatient Consultation"
            default_cpt = "99203"

        # 2. Apply Doctor Seniority Rank Multiplier
        rank_mult = 1.0
        if sched and doctor.rank in sched.rank_multipliers:
            rank_mult = sched.rank_multipliers[doctor.rank]
        unit_price = round(base_fee * rank_mult, 2)

        # 3. Apply Triage Multiplier if in Emergency
        triage_mult = 1.0
        if (is_emergency or encounter.encounter_type == EncounterType.EMERGENCY) and encounter.triage_level:
            triage_mult = self.TRIAGE_MULTIPLIERS.get(encounter.triage_level, 1.0)
            unit_price = round(unit_price * triage_mult, 2)

        # 4. Surcharges (Night / Weekend)
        surcharges_applied = []
        if self.is_night_time(actual_time):
            night_addon = round(unit_price * (self.NIGHT_SURCHARGE_PERCENT / 100.0), 2)
            unit_price += night_addon
            surcharges_applied.append(f"Night Surcharge (+{self.NIGHT_SURCHARGE_PERCENT}%)")

        if self.is_weekend(actual_time):
            weekend_addon = round(unit_price * (self.WEEKEND_SURCHARGE_PERCENT / 100.0), 2)
            unit_price += weekend_addon
            surcharges_applied.append(f"Weekend Surcharge (+{self.WEEKEND_SURCHARGE_PERCENT}%)")

        # 5. Discount Calculation (Follow-up Window check)
        discount_amount = 0.0
        is_followup = self.is_within_followup_window(doctor, actual_time, previous_visit_time)
        if is_followup and sched:
            discount_pct = sched.follow_up_discount_percent
            discount_amount = round(unit_price * (discount_pct / 100.0), 2)

        # Build Line Item
        item = BillingLineItem(
            item_id=str(uuid.uuid4()),
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.CONSULTATION,
            item_code=cpt_code or default_cpt,
            item_name=f"{description_prefix} - {doctor.full_name} ({doctor.specialty_name})",
            description=f"{doctor.rank.value.replace('_', ' ').title()} - {doctor.specialty_name}. " +
                        (f"Surcharges: {', '.join(surcharges_applied)}. " if surcharges_applied else "") +
                        ("Complimentary Follow-up visit." if is_followup and discount_amount == unit_price else ""),
            unit_price=unit_price,
            quantity=1.0,
            subtotal=unit_price,
            discount_amount=discount_amount,
            tax_rate_percent=0.0,  # Healthcare clinical consultations typically 0% tax / exempt
            performed_by_id=doctor.doctor_id,
            metadata={
                "doctor_rank": doctor.rank.value,
                "specialty_code": doctor.specialty_code,
                "triage_level": encounter.triage_level.value if encounter.triage_level else None,
                "is_followup": is_followup,
                "is_night": self.is_night_time(actual_time),
                "is_weekend": self.is_weekend(actual_time),
                "surcharges": surcharges_applied
            }
        )
        item.calculate_totals()
        return item

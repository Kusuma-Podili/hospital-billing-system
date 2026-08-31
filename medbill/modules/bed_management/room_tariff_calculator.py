"""
MedBill Enterprise - Hospital Bed & Inpatient Room Tariff Calculator
Calculates inpatient ward charges, ICU/CCU bed stay, midnight census billing rules,
room transfers, hourly rounding, continuous nursing care, metered oxygen and ventilator billing.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import math
import uuid

from medbill.core.models import (
    Encounter,
    RoomCategoryType,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.catalogs.room_categories import (
    ROOM_TARIFF_CATALOG,
    RoomTariffSchedule,
    get_room_schedule,
)


@dataclass
class RoomStayPeriod:
    category: RoomCategoryType
    start_time: datetime
    end_time: datetime
    metered_oxygen_hours: float = 0.0
    ventilator_hours: float = 0.0
    telemetry_hours: float = 0.0
    infusion_pump_days: float = 0.0
    custom_daily_rate: Optional[float] = None


class RoomBedTariffCalculator:
    """
    Enterprise calculator for inpatient room and bed charges.
    Adheres to midnight census rules and metered intensive care equipment tariffs.
    """

    def __init__(self, room_catalog: Optional[Dict[RoomCategoryType, RoomTariffSchedule]] = None):
        self.room_catalog = room_catalog or ROOM_TARIFF_CATALOG

    def calculate_billable_days_and_hours(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, float]:
        """
        Calculate total duration, calendar midnights crossed, and fractional hours.
        Standard hospital rule: If duration < 24h, bill hourly or minimum 1 day if crossing midnight.
        """
        total_seconds = max(0.0, (end_time - start_time).total_seconds())
        total_hours = total_seconds / 3600.0
        
        # Calendar midnights crossed
        cur_day = start_time.date()
        end_day = end_time.date()
        midnights_crossed = (end_day - cur_day).days

        # Full 24h day equivalent
        calculated_days = total_hours / 24.0
        
        # Hospital standard: At least 1 day or exact days if midnights crossed >= 1
        billable_days = max(1.0, float(midnights_crossed)) if midnights_crossed > 0 else (total_hours / 24.0)

        return {
            "total_hours": round(total_hours, 2),
            "midnights_crossed": midnights_crossed,
            "billable_days": round(billable_days, 2),
            "is_fractional": (total_hours < 24.0 and midnights_crossed == 0)
        }

    def calculate_stay_charges(
        self,
        encounter: Encounter,
        stay_periods: List[RoomStayPeriod]
    ) -> List[BillingLineItem]:
        """
        Generates itemized billing lines for all room stay periods and metered intensive care services.
        """
        line_items: List[BillingLineItem] = []

        for period in stay_periods:
            sched = self.room_catalog.get(period.category)
            if not sched:
                continue

            timing = self.calculate_billable_days_and_hours(period.start_time, period.end_time)
            total_hours = timing["total_hours"]
            billable_days = timing["billable_days"]

            # 1. Base Room Tariff
            if timing["is_fractional"]:
                # Bill at hourly rate for short stay
                unit_price = sched.hourly_rate
                quantity = total_hours
                charge_name = f"Bed Charges (Hourly) - {sched.name}"
                desc = f"Stay from {period.start_time.strftime('%Y-%m-%d %H:%M')} to {period.end_time.strftime('%Y-%m-%d %H:%M')} ({total_hours:.1f} hrs @ ${unit_price:.2f}/hr)"
            else:
                unit_price = period.custom_daily_rate or sched.daily_base_rate
                quantity = billable_days
                charge_name = f"Inpatient Room Rent - {sched.name}"
                desc = f"Stay from {period.start_time.strftime('%Y-%m-%d %H:%M')} to {period.end_time.strftime('%Y-%m-%d %H:%M')} ({billable_days:.1f} days @ ${unit_price:.2f}/day)"

            room_item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=BillingItemCategory.ROOM_BED,
                item_code=f"ROOM_{period.category.value}",
                item_name=charge_name,
                description=desc,
                unit_price=unit_price,
                quantity=quantity,
                subtotal=0.0,
                tax_rate_percent=0.0,
                metadata={
                    "category": period.category.value,
                    "start_time": period.start_time.isoformat(),
                    "end_time": period.end_time.isoformat(),
                    "billable_days": billable_days,
                    "total_hours": total_hours,
                }
            )
            room_item.calculate_totals()
            line_items.append(room_item)

            # 2. Nursing & Resident Doctor Daily Care
            if billable_days > 0:
                nursing_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.NURSING,
                    item_code=f"NURSE_{period.category.value}",
                    item_name=f"24/7 Professional Nursing Care - {sched.name}",
                    description=f"Round-the-clock nursing care for {billable_days:.1f} days",
                    unit_price=sched.nursing_daily_charge,
                    quantity=billable_days,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                nursing_item.calculate_totals()
                line_items.append(nursing_item)

                # Resident Doctor Care & Clinical Monitoring
                resident_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.CONSULTATION,
                    item_code=f"RES_DOC_{period.category.value}",
                    item_name=f"Resident Doctor In-House Care - {sched.name}",
                    description=f"Continuous clinical monitoring by duty medical officer",
                    unit_price=sched.resident_doctor_daily_charge,
                    quantity=billable_days,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                resident_item.calculate_totals()
                line_items.append(resident_item)

                # Biomedical Waste & Sanitization
                bmw_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.MISCELLANEOUS,
                    item_code="BMW_SANITIZATION",
                    item_name="Bio-Medical Waste Management & Room Sterilization",
                    description=f"Sterilization protocol for {billable_days:.1f} days",
                    unit_price=sched.biomedical_waste_daily_charge + sched.housekeeping_daily_charge,
                    quantity=billable_days,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                bmw_item.calculate_totals()
                line_items.append(bmw_item)

            # 3. Metered Medical Gas (Oxygen)
            if period.metered_oxygen_hours > 0:
                o2_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.MEDICAL_GAS,
                    item_code="MED_GAS_O2",
                    item_name="Metered Medical Grade Oxygen Delivery",
                    description=f"Continuous oxygen therapy ({period.metered_oxygen_hours:.1f} hours @ ${sched.oxygen_hourly_rate:.2f}/hr)",
                    unit_price=sched.oxygen_hourly_rate,
                    quantity=period.metered_oxygen_hours,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                o2_item.calculate_totals()
                line_items.append(o2_item)

            # 4. Metered Mechanical Ventilator Support
            if period.ventilator_hours > 0:
                vent_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.EQUIPMENT,
                    item_code="EQUIP_VENTILATOR",
                    item_name="Mechanical Ventilator Support (Invasive/Non-Invasive)",
                    description=f"ICU mechanical ventilator support ({period.ventilator_hours:.1f} hours @ ${sched.ventilator_hourly_rate:.2f}/hr)",
                    unit_price=sched.ventilator_hourly_rate,
                    quantity=period.ventilator_hours,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                vent_item.calculate_totals()
                line_items.append(vent_item)

            # 5. Continuous Cardiac / Telemetry Monitoring
            if period.telemetry_hours > 0:
                telem_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.EQUIPMENT,
                    item_code="EQUIP_TELEMETRY",
                    item_name="Continuous Multipara Cardiac Telemetry Monitoring",
                    description=f"Real-time central hemodynamic monitoring ({period.telemetry_hours:.1f} hours @ ${sched.telemetry_monitoring_hourly_rate:.2f}/hr)",
                    unit_price=sched.telemetry_monitoring_hourly_rate,
                    quantity=period.telemetry_hours,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                telem_item.calculate_totals()
                line_items.append(telem_item)

            # 6. Syringe / Infusion Pumps
            if period.infusion_pump_days > 0:
                pump_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.EQUIPMENT,
                    item_code="EQUIP_INFUSION_PUMP",
                    item_name="Precision Syringe / Infusion Pump Utilization",
                    description=f"Precision continuous IV medication delivery ({period.infusion_pump_days:.1f} days @ ${sched.infusion_pump_daily_rate:.2f}/day)",
                    unit_price=sched.infusion_pump_daily_rate,
                    quantity=period.infusion_pump_days,
                    subtotal=0.0,
                    tax_rate_percent=0.0
                )
                pump_item.calculate_totals()
                line_items.append(pump_item)

        return line_items

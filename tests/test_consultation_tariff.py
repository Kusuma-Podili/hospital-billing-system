"""
MedBill Enterprise - Automated Test Suite 1: Consultation Tariff Calculation
Validates doctor consultation charges, rank multipliers, triage surcharges,
night/weekend surcharges, and follow-up validity window calculations.
"""

import unittest
from datetime import datetime, timedelta
import uuid

from medbill.core.models import (
    Doctor,
    DoctorRank,
    Encounter,
    EncounterType,
    TriageLevel,
    BillingItemCategory,
)
from medbill.modules.consultation.consultation_calculator import ConsultationTariffCalculator
from medbill.catalogs.doctors_specialties import SPECIALTY_CATALOG


class TestConsultationTariffCalculation(unittest.TestCase):

    def setUp(self):
        self.calculator = ConsultationTariffCalculator()
        self.cardiologist = Doctor(
            doctor_id="DOC_CARDIO_01",
            license_number="MD-CARDIO-8891",
            first_name="Arthur",
            last_name="Pendelton",
            specialty_code="CARDIO",
            specialty_name="Cardiology & Interventional Cardiology",
            rank=DoctorRank.SENIOR_CONSULTANT,
            base_consultation_fee=150.00,
            telemedicine_fee=120.00,
            department_id="DEPT_CARDIO"
        )
        self.general_physician = Doctor(
            doctor_id="DOC_GEN_01",
            license_number="MD-GEN-1029",
            first_name="Sarah",
            last_name="Connor",
            specialty_code="GEN_MED",
            specialty_name="Internal Medicine / General Physician",
            rank=DoctorRank.ATTENDING_PHYSICIAN,
            base_consultation_fee=75.00,
            telemedicine_fee=60.00,
            department_id="DEPT_MED"
        )

    def test_standard_outpatient_consultation_with_rank_multiplier(self):
        """Test standard OPD visit with Senior Consultant 1.4x rank multiplier."""
        # A Tuesday morning visit at 10:00 AM (weekday, day time)
        visit_time = datetime(2026, 9, 1, 10, 0, 0)
        encounter = Encounter(
            encounter_id="ENC_OPD_001",
            patient_id="PAT_1001",
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=visit_time
        )

        item = self.calculator.calculate_consultation_charge(
            doctor=self.cardiologist,
            encounter=encounter,
            visit_time=visit_time
        )

        # Base fee = 150.00 * Senior Consultant (1.40) = 210.00
        expected_fee = round(150.00 * 1.40, 2)
        self.assertEqual(item.category, BillingItemCategory.CONSULTATION)
        self.assertEqual(item.unit_price, expected_fee)
        self.assertEqual(item.total_amount, expected_fee)
        self.assertEqual(item.discount_amount, 0.0)

    def test_emergency_triage_level_1_resuscitation(self):
        """Test emergency presentation with Level 1 Resuscitation (2.5x multiplier)."""
        visit_time = datetime(2026, 9, 2, 14, 0, 0)  # Wednesday afternoon
        encounter = Encounter(
            encounter_id="ENC_ER_001",
            patient_id="PAT_1002",
            encounter_type=EncounterType.EMERGENCY,
            admission_time=visit_time,
            triage_level=TriageLevel.LEVEL_1_RESUSCITATION
        )

        item = self.calculator.calculate_consultation_charge(
            doctor=self.cardiologist,
            encounter=encounter,
            visit_time=visit_time,
            is_emergency=True
        )

        # Emergency on-call base = 300.00
        # Rank multiplier (Senior Consultant) = 1.40 -> 420.00
        # Level 1 Triage multiplier = 2.50 -> 1050.00
        expected_fee = round(300.00 * 1.40 * 2.50, 2)
        self.assertEqual(item.unit_price, expected_fee)
        self.assertEqual(item.total_amount, expected_fee)

    def test_night_and_weekend_surcharge_calculation(self):
        """Test night time (8 PM - 7 AM) and weekend surcharges."""
        # Saturday night at 23:30 (Weekend + Night)
        visit_time = datetime(2026, 9, 5, 23, 30, 0)
        encounter = Encounter(
            encounter_id="ENC_OPD_002",
            patient_id="PAT_1003",
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=visit_time
        )

        item = self.calculator.calculate_consultation_charge(
            doctor=self.general_physician,
            encounter=encounter,
            visit_time=visit_time
        )

        # Base fee = 75.00 * 1.0 (Attending) = 75.00
        # Night surcharge = +30% (+22.50) -> 97.50
        # Weekend surcharge = +20% (+19.50) -> 117.00
        expected_fee = round((75.00 * 1.30) * 1.20, 2)
        self.assertEqual(item.unit_price, expected_fee)
        self.assertTrue("Night Surcharge" in item.description)
        self.assertTrue("Weekend Surcharge" in item.description)

    def test_complimentary_followup_window_discount(self):
        """Test that follow-up visits within validity window receive 100% discount."""
        initial_visit = datetime(2026, 9, 1, 10, 0, 0)
        followup_visit = datetime(2026, 9, 4, 11, 0, 0)  # 3 days later on Friday (within 7-day window)

        encounter = Encounter(
            encounter_id="ENC_OPD_003",
            patient_id="PAT_1004",
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=followup_visit
        )

        item = self.calculator.calculate_consultation_charge(
            doctor=self.cardiologist,
            encounter=encounter,
            visit_time=followup_visit,
            previous_visit_time=initial_visit
        )

        # Subtotal is 210.00, but discount is 210.00, resulting in $0.00 total
        self.assertEqual(item.subtotal, 210.00)
        self.assertEqual(item.discount_amount, 210.00)
        self.assertEqual(item.total_amount, 0.0)
        self.assertTrue(item.metadata["is_followup"])

    def test_telemedicine_consultation(self):
        """Test telemedicine consultation pricing."""
        visit_time = datetime(2026, 9, 2, 16, 0, 0)
        encounter = Encounter(
            encounter_id="ENC_TELE_001",
            patient_id="PAT_1005",
            encounter_type=EncounterType.TELEMEDICINE,
            admission_time=visit_time
        )

        item = self.calculator.calculate_consultation_charge(
            doctor=self.cardiologist,
            encounter=encounter,
            visit_time=visit_time,
            is_telemedicine=True
        )

        # Telemedicine base fee = 120.00 * 1.40 rank mult = 168.00
        expected_fee = round(120.00 * 1.40, 2)
        self.assertEqual(item.unit_price, expected_fee)
        self.assertEqual(item.total_amount, expected_fee)


if __name__ == "__main__":
    unittest.main()

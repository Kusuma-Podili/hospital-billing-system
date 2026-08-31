"""
MedBill Enterprise - Automated Test Suite 6: Insurance & TPA Claim Adjudication
Validates contractual in-network discounts, deductible accumulators, co-pay deductions,
co-insurance 80/20 calculations, out-of-pocket maximum (OOPM) capping, and pre-auth denials.
"""

import unittest
from datetime import datetime

from medbill.core.models import (
    Patient,
    PatientGender,
    Encounter,
    EncounterType,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.modules.insurance_tpa.models import (
    InsurancePolicy,
    PlanType,
    AdjudicationStatus,
)
from medbill.modules.insurance_tpa.claims_engine import InsuranceClaimsEngine


class TestInsuranceAdjudication(unittest.TestCase):

    def setUp(self):
        self.engine = InsuranceClaimsEngine()
        self.patient = Patient(
            patient_id="PAT_INS_001",
            mrn="MRN-88291",
            first_name="Jane",
            last_name="Doe",
            dob="1985-06-15",
            gender=PatientGender.FEMALE,
            phone="555-0192",
            email="jane.doe@example.com",
            address="100 Medical Blvd, City, State"
        )
        self.policy = InsurancePolicy(
            policy_id="POL_BLUE_CROSS_PPO",
            patient_id="PAT_INS_001",
            payer_id="PAYER_BCBS_01",
            payer_name="Blue Cross Blue Shield",
            plan_name="Premier PPO Gold 80/20",
            plan_type=PlanType.PPO,
            group_number="GRP-99881",
            member_id="MBR-12345678",
            annual_deductible=500.00,
            deductible_met=0.00,
            annual_out_of_pocket_max=3000.00,
            out_of_pocket_met=0.00,
            coinsurance_rate=0.20,  # 20% patient responsibility
            copay_general_opd=20.00,
            copay_specialist_opd=40.00,
            contractual_discount_percent=10.00  # 10% in-network discount
        )

    def test_outpatient_specialist_visit_adjudication(self):
        """Test Outpatient Specialist Visit ($200 billed - 10% discount = $180 allowed). Copay $40, then deductible applied."""
        encounter = Encounter(
            encounter_id="ENC_OPD_INS_01",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=datetime(2026, 9, 1, 10, 0, 0)
        )

        item = BillingLineItem(
            item_id="ITEM_001",
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.CONSULTATION,
            item_code="99204",
            item_name="Cardiology Specialist Consultation",
            description="Specialist consultation",
            unit_price=200.00,
            quantity=1.0,
            subtotal=200.00,
            total_amount=200.00
        )

        adj = self.engine.adjudicate_claim(
            encounter=encounter,
            patient=self.patient,
            policy=self.policy,
            line_items=[item]
        )

        self.assertEqual(adj.total_billed, 200.00)
        self.assertEqual(adj.total_contractual_discount, 20.00)  # 10% of 200
        self.assertEqual(adj.total_allowed, 180.00)
        self.assertEqual(adj.total_copay, 40.00)
        # Remaining after copay = 140.00 -> goes towards $500 deductible
        self.assertEqual(adj.total_deductible, 140.00)
        self.assertEqual(adj.total_payer_paid, 0.00)
        # Patient pays Copay $40 + Deductible $140 = $180.00
        self.assertEqual(adj.total_patient_responsibility, 180.00)

    def test_deductible_exhaustion_and_coinsurance_split(self):
        """Test scenario where deductible is already fully met and 80/20 coinsurance applies."""
        # Set deductible as already fully satisfied
        self.policy.deductible_met = 500.00
        encounter = Encounter(
            encounter_id="ENC_LAB_INS_01",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=datetime(2026, 9, 1, 11, 0, 0)
        )

        item = BillingLineItem(
            item_id="ITEM_002",
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.LABORATORY,
            item_code="80053",
            item_name="Comprehensive Metabolic Panel",
            description="Blood test",
            unit_price=100.00,
            quantity=1.0,
            subtotal=100.00,
            total_amount=100.00
        )

        adj = self.engine.adjudicate_claim(
            encounter=encounter,
            patient=self.patient,
            policy=self.policy,
            line_items=[item]
        )

        # $100 billed - 10% discount = $90 allowed
        # Deductible met -> 0 deductible
        # Coinsurance: 20% patient ($18.00), 80% insurer ($72.00)
        self.assertEqual(adj.total_allowed, 90.00)
        self.assertEqual(adj.total_deductible, 0.00)
        self.assertEqual(adj.total_coinsurance, 18.00)
        self.assertEqual(adj.total_payer_paid, 72.00)
        self.assertEqual(adj.total_patient_responsibility, 18.00)

    def test_out_of_pocket_maximum_capping(self):
        """Test that when OOPM is met, patient pays $0 and insurer pays 100% of allowed amount."""
        # Patient already met $3,000 OOPM limit
        self.policy.deductible_met = 500.00
        self.policy.out_of_pocket_met = 3000.00

        encounter = Encounter(
            encounter_id="ENC_IPD_INS_01",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime(2026, 9, 1, 8, 0, 0)
        )

        item = BillingLineItem(
            item_id="ITEM_003",
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.ROOM_BED,
            item_code="ROOM_DELUXE",
            item_name="Inpatient Stay",
            description="Room charge",
            unit_price=2000.00,
            quantity=1.0,
            subtotal=2000.00,
            total_amount=2000.00
        )

        adj = self.engine.adjudicate_claim(
            encounter=encounter,
            patient=self.patient,
            policy=self.policy,
            line_items=[item],
            pre_authorization_code="AUTH-9901-APPROVED"
        )

        # Billed $2000 - 10% = $1800 allowed. Patient OOP met -> Patient pays $0, Insurer pays $1800.
        self.assertEqual(adj.total_allowed, 1800.00)
        self.assertEqual(adj.total_patient_responsibility, 0.00)
        self.assertEqual(adj.total_payer_paid, 1800.00)
        self.assertEqual(adj.status, AdjudicationStatus.APPROVED)

    def test_missing_pre_authorization_rejection(self):
        """Test that inpatient claim exceeding threshold without pre-auth is flagged REQUIRES_PRE_AUTH."""
        encounter = Encounter(
            encounter_id="ENC_IPD_INS_02",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime(2026, 9, 1, 8, 0, 0)
        )

        item = BillingLineItem(
            item_id="ITEM_004",
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.SURGERY,
            item_code="27447",
            item_name="Total Knee Replacement",
            description="Surgery",
            unit_price=5000.00,
            quantity=1.0,
            subtotal=5000.00,
            total_amount=5000.00
        )

        adj = self.engine.adjudicate_claim(
            encounter=encounter,
            patient=self.patient,
            policy=self.policy,
            line_items=[item],
            pre_authorization_code=None  # Missing pre-auth!
        )

        self.assertEqual(adj.status, AdjudicationStatus.REQUIRES_PRE_AUTH)
        self.assertEqual(adj.total_payer_paid, 0.00)
        self.assertTrue("Pre-authorization required" in adj.explanation_of_benefits_notes)


if __name__ == "__main__":
    unittest.main()

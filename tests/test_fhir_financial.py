"""
MedBill Enterprise - Automated Test Suite 7: HL7 FHIR R4 Financial Integration
Validates schema compliance of FHIR R4 Account, Coverage, Claim, and ExplanationOfBenefit resources.
"""

import unittest
from datetime import datetime
import json

from medbill.core.models import (
    Patient,
    PatientGender,
    Encounter,
    EncounterType,
    BillingLineItem,
    BillingItemCategory,
    Invoice,
    InvoiceStatus,
)
from medbill.modules.insurance_tpa.models import (
    InsurancePolicy,
    PlanType,
    AdjudicationStatus,
    AdjudicationSummary,
)
from medbill.modules.fhir.fhir_financial import FHIRFinancialResourceBuilder


class TestFHIRFinancialResources(unittest.TestCase):

    def setUp(self):
        self.patient = Patient(
            patient_id="PAT_FHIR_01",
            mrn="MRN-FHIR-100",
            first_name="Robert",
            last_name="Langdon",
            dob="1970-04-12",
            gender=PatientGender.MALE,
            phone="555-4321",
            email="robert.l@example.com",
            address="Harvard Yard, Cambridge, MA"
        )
        self.policy = InsurancePolicy(
            policy_id="POL_AETNA_01",
            patient_id=self.patient.patient_id,
            payer_id="PAYER_AETNA",
            payer_name="Aetna Healthcare",
            plan_name="Aetna Choice POS II",
            plan_type=PlanType.POS,
            group_number="GRP-AETNA-77",
            member_id="MBR-987654",
            annual_deductible=1000.00,
            deductible_met=250.00,
            annual_out_of_pocket_max=5000.00,
            out_of_pocket_met=600.00,
            coinsurance_rate=0.20
        )

    def test_fhir_account_resource_generation(self):
        """Test FHIR R4 Account resource structure."""
        invoice = Invoice(
            invoice_id="INV-9901",
            invoice_number="INV-2026-0001",
            encounter_id="ENC-001",
            patient_id=self.patient.patient_id,
            issue_date="2026-09-01",
            due_date="2026-10-01",
            status=InvoiceStatus.APPROVED,
            balance_due=450.00,
            currency="USD"
        )

        account = FHIRFinancialResourceBuilder.build_account_resource(invoice, self.patient, self.policy)

        self.assertEqual(account["resourceType"], "Account")
        self.assertEqual(account["status"], "active")
        self.assertEqual(account["subject"][0]["reference"], f"Patient/{self.patient.patient_id}")
        self.assertEqual(account["balance"][0]["amount"], 450.00)
        self.assertEqual(account["balance"][0]["currency"], "USD")

    def test_fhir_coverage_resource_generation(self):
        """Test FHIR R4 Coverage resource structure."""
        coverage = FHIRFinancialResourceBuilder.build_coverage_resource(self.patient, self.policy)

        self.assertEqual(coverage["resourceType"], "Coverage")
        self.assertEqual(coverage["status"], "active")
        self.assertEqual(coverage["subscriber"]["reference"], f"Patient/{self.patient.patient_id}")
        self.assertEqual(coverage["payor"][0]["display"], "Aetna Healthcare")
        self.assertEqual(coverage["class"][0]["value"], "GRP-AETNA-77")

    def test_fhir_claim_resource_generation(self):
        """Test FHIR R4 Claim resource structure."""
        encounter = Encounter(
            encounter_id="ENC-FHIR-01",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=datetime(2026, 9, 1, 9, 0, 0),
            primary_icd10_code="I10"
        )

        item = BillingLineItem(
            item_id="ITEM-1",
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.CONSULTATION,
            item_code="99214",
            item_name="Office Visit Moderate MDM",
            description="Consultation",
            unit_price=190.00,
            quantity=1.0,
            subtotal=190.00,
            total_amount=190.00
        )

        claim = FHIRFinancialResourceBuilder.build_claim_resource(
            encounter=encounter,
            patient=self.patient,
            policy=self.policy,
            line_items=[item]
        )

        self.assertEqual(claim["resourceType"], "Claim")
        self.assertEqual(claim["patient"]["reference"], f"Patient/{self.patient.patient_id}")
        self.assertEqual(claim["diagnosis"][0]["diagnosisCodeableConcept"]["coding"][0]["code"], "I10")
        self.assertEqual(claim["item"][0]["productOrService"]["coding"][0]["code"], "99214")
        self.assertEqual(claim["total"]["value"], 190.00)

    def test_fhir_explanation_of_benefit_generation(self):
        """Test FHIR R4 ExplanationOfBenefit (EOB) resource."""
        adj = AdjudicationSummary(
            claim_id="CLM-EOB-881",
            encounter_id="ENC-001",
            policy_id=self.policy.policy_id,
            payer_name=self.policy.payer_name,
            total_billed=500.00,
            total_contractual_discount=50.00,
            total_allowed=450.00,
            total_deductible=100.00,
            total_copay=40.00,
            total_coinsurance=62.00,
            total_payer_paid=248.00,
            total_patient_responsibility=202.00,
            status=AdjudicationStatus.APPROVED
        )

        eob = FHIRFinancialResourceBuilder.build_explanation_of_benefit_resource(adj, self.patient)

        self.assertEqual(eob["resourceType"], "ExplanationOfBenefit")
        self.assertEqual(eob["insurer"]["display"], "Aetna Healthcare")
        self.assertEqual(eob["total"][0]["amount"]["value"], 500.00)
        self.assertEqual(eob["total"][1]["amount"]["value"], 248.00)
        self.assertEqual(eob["total"][2]["amount"]["value"], 202.00)


if __name__ == "__main__":
    unittest.main()

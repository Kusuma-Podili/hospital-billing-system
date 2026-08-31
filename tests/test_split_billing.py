"""
MedBill Enterprise - Automated Test Suite 9: Multi-Payer Split Billing
Validates invoice aggregation across all departments and multi-payer split allocation
(Primary Insurer, Corporate Subsidy, Hardship Waiver, Patient Out-of-Pocket).
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
    InvoiceStatus,
    PaymentMethod,
)
from medbill.modules.insurance_tpa.models import (
    AdjudicationSummary,
    AdjudicationStatus,
)
from medbill.modules.billing_engine.master_invoice_aggregator import MasterInvoiceAggregator


class TestSplitBilling(unittest.TestCase):

    def setUp(self):
        self.aggregator = MasterInvoiceAggregator()
        self.patient = Patient(
            patient_id="PAT_SPLIT_01",
            mrn="MRN-SPLIT-99",
            first_name="Alice",
            last_name="Wonderland",
            dob="1990-01-01",
            gender=PatientGender.FEMALE,
            phone="555-9876",
            email="alice@example.com",
            address="42 Rabbit Hole Lane"
        )
        self.encounter = Encounter(
            encounter_id="ENC_SPLIT_01",
            patient_id=self.patient.patient_id,
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime(2026, 9, 1, 8, 0, 0)
        )

    def test_multi_payer_split_insurance_corporate_and_patient(self):
        """Test multi-payer split: Total $10,000 -> Insurer pays $7,000 -> Corporate Sponsor pays 50% of remainder ($1,500) -> Patient pays $1,500."""
        items = [
            BillingLineItem(
                item_id="ITEM-1",
                encounter_id=self.encounter.encounter_id,
                category=BillingItemCategory.SURGERY,
                item_code="27447",
                item_name="Knee Surgery",
                description="Procedure",
                unit_price=10000.00,
                quantity=1.0,
                subtotal=10000.00,
                total_amount=10000.00
            )
        ]

        mock_adjudication = AdjudicationSummary(
            claim_id="CLM-SPLIT-1",
            encounter_id=self.encounter.encounter_id,
            policy_id="POL-1",
            payer_name="UnitedHealth",
            total_billed=10000.00,
            total_contractual_discount=0.0,
            total_allowed=10000.00,
            total_deductible=0.0,
            total_copay=0.0,
            total_coinsurance=3000.00,
            total_payer_paid=7000.00,
            total_patient_responsibility=3000.00,
            status=AdjudicationStatus.APPROVED
        )

        invoice = self.aggregator.create_master_invoice(
            encounter=self.encounter,
            patient=self.patient,
            line_items=items,
            adjudication=mock_adjudication,
            sponsor_share_percent=50.0  # Employer covers 50% of patient balance
        )

        self.assertEqual(invoice.gross_total, 10000.00)
        self.assertEqual(invoice.insurance_payable, 7000.00)
        self.assertEqual(invoice.sponsor_payable, 1500.00)  # 50% of 3000
        self.assertEqual(invoice.patient_payable, 1500.00)  # Remaining 50% of 3000
        self.assertEqual(invoice.balance_due, 10000.00)

    def test_charity_care_hardship_waiver(self):
        """Test financial hardship waiver (30% indigent subsidy discount)."""
        items = [
            BillingLineItem(
                item_id="ITEM-2",
                encounter_id=self.encounter.encounter_id,
                category=BillingItemCategory.CONSULTATION,
                item_code="99203",
                item_name="Consultation",
                description="Doctor visit",
                unit_price=1000.00,
                quantity=1.0,
                subtotal=1000.00,
                total_amount=1000.00
            )
        ]

        invoice = self.aggregator.create_master_invoice(
            encounter=self.encounter,
            patient=self.patient,
            line_items=items,
            adjudication=None,
            hardship_discount_percent=30.0  # 30% hardship discount
        )

        # Gross $1000 - $300 discount = $700 patient payable
        self.assertEqual(invoice.total_discount, 300.00)
        self.assertEqual(invoice.patient_payable, 700.00)

    def test_payment_recording_and_invoice_closure(self):
        """Test recording partial payment and final settlement."""
        items = [
            BillingLineItem(
                item_id="ITEM-3",
                encounter_id=self.encounter.encounter_id,
                category=BillingItemCategory.PHARMACY,
                item_code="DRUG-1",
                item_name="Medication",
                description="Antibiotics",
                unit_price=500.00,
                quantity=1.0,
                subtotal=500.00,
                total_amount=500.00
            )
        ]

        invoice = self.aggregator.create_master_invoice(
            encounter=self.encounter,
            patient=self.patient,
            line_items=items
        )

        # 1. Partial payment of $200
        pmt1 = self.aggregator.record_payment(invoice, 200.00, PaymentMethod.CASH)
        self.assertEqual(invoice.paid_amount, 200.00)
        self.assertEqual(invoice.balance_due, 300.00)
        self.assertEqual(invoice.status, InvoiceStatus.PARTIALLY_PAID)

        # 2. Final payment of $300
        pmt2 = self.aggregator.record_payment(invoice, 300.00, PaymentMethod.UPI)
        self.assertEqual(invoice.paid_amount, 500.00)
        self.assertEqual(invoice.balance_due, 0.00)
        self.assertEqual(invoice.status, InvoiceStatus.PAID)


if __name__ == "__main__":
    unittest.main()

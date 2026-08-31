"""
MedBill Enterprise - Automated Test Suite 3: Pharmacy Dispensing & Medication Billing
Validates medication selling prices, prescription batch tracking, tax calculation (5%),
compounding fees, and expired lot safety checks.
"""

import unittest
from datetime import datetime, date, timedelta

from medbill.core.models import (
    Encounter,
    EncounterType,
    BillingItemCategory,
)
from medbill.modules.pharmacy.pharmacy_calculator import (
    PrescriptionOrder,
    PharmacyTariffCalculator,
)
from medbill.catalogs.pharmacy_ndc import PHARMACY_NDC_CATALOG


class TestPharmacyBilling(unittest.TestCase):

    def setUp(self):
        self.calculator = PharmacyTariffCalculator()
        self.encounter = Encounter(
            encounter_id="ENC_PHARM_001",
            patient_id="PAT_3001",
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime(2026, 9, 1, 9, 0, 0)
        )

    def test_standard_medication_dispensing_with_tax(self):
        """Test dispensing Augmentin 875mg (10 tabs @ $4.50 = $45.00 + 5% tax = $47.25)."""
        future_expiry = (date.today() + timedelta(days=365)).strftime("%Y-%m-%d")
        order = PrescriptionOrder(
            ndc="00093-3147-01",  # Augmentin 875mg
            quantity=10.0,
            batch_number="LOT-AUG-9921",
            expiry_date=future_expiry,
            prescribed_by_doctor_id="DOC_GEN_01"
        )

        items = self.calculator.dispense_medications(self.encounter, [order])

        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item.category, BillingItemCategory.PHARMACY)
        self.assertEqual(item.quantity, 10.0)
        self.assertEqual(item.unit_price, 4.50)
        self.assertEqual(item.subtotal, 45.00)
        self.assertEqual(item.tax_rate_percent, 5.0)
        self.assertEqual(item.tax_amount, 2.25)
        self.assertEqual(item.total_amount, 47.25)
        self.assertEqual(item.metadata["batch_number"], "LOT-AUG-9921")

    def test_sterile_iv_compounding_and_stat_delivery(self):
        """Test IV Vancomycin with sterile compounding fee ($15) and STAT urgent delivery ($10)."""
        future_expiry = (date.today() + timedelta(days=180)).strftime("%Y-%m-%d")
        order = PrescriptionOrder(
            ndc="00074-6332-11",  # Vancomycin 1g IV
            quantity=2.0,
            batch_number="LOT-VANCO-404",
            expiry_date=future_expiry,
            prescribed_by_doctor_id="DOC_ICU_01",
            is_compounded_iv=True,
            is_stat_urgent=True
        )

        items = self.calculator.dispense_medications(self.encounter, [order])

        # Expect 3 items: Drug + Compounding fee + STAT fee
        self.assertEqual(len(items), 3)

        drug_item = items[0]
        # 2 vials @ $32.00 = $64.00 + 5% tax ($3.20) = $67.20
        self.assertEqual(drug_item.subtotal, 64.00)
        self.assertEqual(drug_item.total_amount, 67.20)

        comp_item = items[1]
        self.assertEqual(comp_item.item_code, "PHARM_COMPOUNDING")
        self.assertEqual(comp_item.total_amount, 15.00)

        stat_item = items[2]
        self.assertEqual(stat_item.item_code, "PHARM_STAT_DELIVERY")
        self.assertEqual(stat_item.total_amount, 10.00)

    def test_controlled_substance_flagging(self):
        """Test that Schedule II Opioid (Fentanyl) is flagged as controlled substance."""
        future_expiry = (date.today() + timedelta(days=200)).strftime("%Y-%m-%d")
        order = PrescriptionOrder(
            ndc="00045-0255-10",  # Fentanyl Citrate 100mcg
            quantity=3.0,
            batch_number="LOT-FENT-001",
            expiry_date=future_expiry,
            prescribed_by_doctor_id="DOC_ANESTH_01"
        )

        items = self.calculator.dispense_medications(self.encounter, [order])
        item = items[0]
        self.assertTrue(item.metadata["is_controlled"])
        self.assertEqual(item.metadata["dea_schedule"], "Schedule II")

    def test_expired_batch_rejection(self):
        """Test that dispensing an expired medication batch raises ValueError."""
        past_expiry = (date.today() - timedelta(days=10)).strftime("%Y-%m-%d")
        order = PrescriptionOrder(
            ndc="00093-3147-01",
            quantity=5.0,
            batch_number="LOT-EXPIRED-999",
            expiry_date=past_expiry,
            prescribed_by_doctor_id="DOC_GEN_01"
        )

        with self.assertRaises(ValueError):
            self.calculator.dispense_medications(self.encounter, [order])


if __name__ == "__main__":
    unittest.main()

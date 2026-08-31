"""
MedBill Enterprise - Automated Test Suite 4: Laboratory & Diagnostic Radiology Billing
Validates LOINC panel pricing, urgent STAT multipliers (+50%), pathologist/radiologist review fees,
and multi-panel bundle discounts.
"""

import unittest
from datetime import datetime

from medbill.core.models import (
    Encounter,
    EncounterType,
    BillingItemCategory,
)
from medbill.modules.laboratory.lab_tariff_calculator import (
    DiagnosticOrder,
    LabTariffCalculator,
)
from medbill.catalogs.loinc_lab_panels import LOINC_LAB_CATALOG


class TestLabDiagnostics(unittest.TestCase):

    def setUp(self):
        self.calculator = LabTariffCalculator()
        self.encounter = Encounter(
            encounter_id="ENC_LAB_001",
            patient_id="PAT_4001",
            encounter_type=EncounterType.OUTPATIENT,
            admission_time=datetime(2026, 9, 1, 10, 30, 0)
        )

    def test_routine_blood_panel_with_phlebotomy_and_pathologist_review(self):
        """Test routine CBC panel (Test $45 + Phlebotomy $12 + Pathologist $15 = $72)."""
        order = DiagnosticOrder(
            loinc_code="58410-2",  # CBC
            is_stat_urgent=False,
            ordering_doctor_id="DOC_GEN_01"
        )

        items = self.calculator.calculate_diagnostic_orders(self.encounter, [order])

        # Expect 3 line items: Test charge + Phlebotomy fee + Pathologist report
        self.assertEqual(len(items), 3)

        test_item = next(i for i in items if i.item_code == "58410-2")
        self.assertEqual(test_item.category, BillingItemCategory.LABORATORY)
        self.assertEqual(test_item.total_amount, 45.00)

        phleb_item = next(i for i in items if i.item_code == "PHLEBOTOMY_FEE")
        self.assertEqual(phleb_item.total_amount, 12.00)

        path_item = next(i for i in items if i.item_code.startswith("PROF_READ_"))
        self.assertEqual(path_item.total_amount, 15.00)

    def test_urgent_stat_cardiac_troponin_multiplier(self):
        """Test urgent STAT high-sensitivity Troponin-I (Base $85 * 1.60 STAT = $136.00)."""
        order = DiagnosticOrder(
            loinc_code="6598-7",  # hs-cTnI
            is_stat_urgent=True,
            ordering_doctor_id="DOC_CARDIO_01"
        )

        items = self.calculator.calculate_diagnostic_orders(self.encounter, [order])

        test_item = next(i for i in items if i.item_code == "6598-7")
        # 85.00 * 1.60 = 136.00
        self.assertEqual(test_item.unit_price, 136.00)
        self.assertEqual(test_item.total_amount, 136.00)
        self.assertTrue("STAT" in test_item.description)

    def test_diagnostic_radiology_mri_brain(self):
        """Test 3T MRI Brain ($1150 + Radiologist Report $220 = $1370)."""
        order = DiagnosticOrder(
            loinc_code="24590-2",  # MRI Brain with Contrast
            is_stat_urgent=False,
            ordering_doctor_id="DOC_NEURO_01"
        )

        items = self.calculator.calculate_diagnostic_orders(self.encounter, [order])

        mri_item = next(i for i in items if i.item_code == "24590-2")
        self.assertEqual(mri_item.category, BillingItemCategory.RADIOLOGY)
        self.assertEqual(mri_item.total_amount, 1150.00)

        rad_item = next(i for i in items if i.item_code == "PROF_READ_24590-2")
        self.assertEqual(rad_item.category, BillingItemCategory.RADIOLOGY)
        self.assertEqual(rad_item.total_amount, 220.00)

    def test_multi_panel_bundle_discount(self):
        """Test that ordering 3 or more lab panels automatically applies 10% bundle discount."""
        orders = [
            DiagnosticOrder(loinc_code="58410-2"),  # CBC ($45)
            DiagnosticOrder(loinc_code="24323-8"),  # CMP ($65)
            DiagnosticOrder(loinc_code="24331-1"),  # Lipid ($55)
        ]

        items = self.calculator.calculate_diagnostic_orders(self.encounter, orders)

        cbc_item = next(i for i in items if i.item_code == "58410-2")
        # $45 - 10% ($4.50) = $40.50
        self.assertEqual(cbc_item.discount_amount, 4.50)
        self.assertEqual(cbc_item.total_amount, 40.50)

        cmp_item = next(i for i in items if i.item_code == "24323-8")
        # $65 - 10% ($6.50) = $58.50
        self.assertEqual(cmp_item.discount_amount, 6.50)
        self.assertEqual(cmp_item.total_amount, 58.50)


if __name__ == "__main__":
    unittest.main()

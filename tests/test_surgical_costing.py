"""
MedBill Enterprise - Automated Test Suite 5: Surgical Procedure & Operating Theater Costing
Validates major surgery costing, OT table hourly tiers, Chief Surgeon fees, Anesthesiologist fees,
consumables kits, implants, and PACU recovery room billing.
"""

import unittest
from datetime import datetime

from medbill.core.models import (
    Encounter,
    EncounterType,
    BillingItemCategory,
)
from medbill.modules.surgery.surgical_costing_calculator import (
    SurgeryExecutionDetails,
    SurgicalCostingCalculator,
)
from medbill.catalogs.surgical_packages import SURGERY_CATALOG


class TestSurgicalCosting(unittest.TestCase):

    def setUp(self):
        self.calculator = SurgicalCostingCalculator()
        self.encounter = Encounter(
            encounter_id="ENC_SURG_001",
            patient_id="PAT_5001",
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime(2026, 9, 1, 7, 0, 0)
        )

    def test_laparoscopic_cholecystectomy_surgical_package(self):
        """Test standard 2-hour Laparoscopic Cholecystectomy (OT $700 + Surgeon $1800 + Anesth $650 + Co-Surgeon $450 + Consumables $550 + PACU $160)."""
        surgery = SurgeryExecutionDetails(
            procedure_code="47562",  # Lap Chole
            actual_duration_hours=2.0,
            chief_surgeon_id="DOC_SURG_01",
            anesthesiologist_id="DOC_ANESTH_01",
            co_surgeon_id="DOC_SURG_RES_01",
            pacu_recovery_hours=2.0
        )

        items = self.calculator.calculate_surgical_episode(self.encounter, surgery)

        # 1. OT Table: 2.0 hrs @ $350/hr = $700.00
        ot_item = next(i for i in items if i.item_code.startswith("OT_RENT_"))
        self.assertEqual(ot_item.total_amount, 700.00)

        # 2. Chief Surgeon: $1800.00
        surgeon_item = next(i for i in items if i.item_code.startswith("SURGEON_FEE_"))
        self.assertEqual(surgeon_item.total_amount, 1800.00)

        # 3. Co-Surgeon: $450.00
        co_item = next(i for i in items if i.item_code.startswith("CO_SURGEON_"))
        self.assertEqual(co_item.total_amount, 450.00)

        # 4. Anesthesiologist: $650.00
        anesth_item = next(i for i in items if i.category == BillingItemCategory.ANESTHESIA)
        self.assertEqual(anesth_item.total_amount, 650.00)

        # 5. Consumables: $550.00
        kit_item = next(i for i in items if i.item_code.startswith("SURG_KIT_"))
        self.assertEqual(kit_item.total_amount, 550.00)

        # 6. PACU Stay: 2.0 hrs @ $80/hr = $160.00
        pacu_item = next(i for i in items if i.item_code == "PACU_RECOVERY")
        self.assertEqual(pacu_item.total_amount, 160.00)

        total_surgery = sum(i.total_amount for i in items)
        self.assertEqual(total_surgery, 700 + 1800 + 450 + 650 + 550 + 160)

    def test_total_knee_replacement_with_implant(self):
        """Test Total Knee Replacement (TKR) with titanium prosthetic knee implant ($3200 + 5% tax)."""
        surgery = SurgeryExecutionDetails(
            procedure_code="27447",  # Total Knee Arthroplasty
            actual_duration_hours=3.0,
            chief_surgeon_id="DOC_ORTHO_01",
            anesthesiologist_id="DOC_ANESTH_01",
            actual_implant_cost=3200.00,
            implant_serial_number="IMPL-KNEE-TITAN-883",
            pacu_recovery_hours=2.0
        )

        items = self.calculator.calculate_surgical_episode(self.encounter, surgery)

        implant_item = next(i for i in items if i.item_code.startswith("IMPLANT_"))
        self.assertEqual(implant_item.subtotal, 3200.00)
        self.assertEqual(implant_item.tax_rate_percent, 5.0)
        self.assertEqual(implant_item.tax_amount, 160.00)
        self.assertEqual(implant_item.total_amount, 3360.00)
        self.assertEqual(implant_item.metadata["serial_number"], "IMPL-KNEE-TITAN-883")

    def test_emergency_surgery_surcharge(self):
        """Test emergency out-of-hours craniotomy with +25% emergency surgeon & OT surcharge."""
        surgery = SurgeryExecutionDetails(
            procedure_code="61154",  # Craniotomy for Subdural Hematoma
            actual_duration_hours=4.0,
            chief_surgeon_id="DOC_NEURO_SURG_01",
            anesthesiologist_id="DOC_ANESTH_01",
            is_emergency_surgery=True
        )

        items = self.calculator.calculate_surgical_episode(self.encounter, surgery)

        # Base Chief Surgeon fee is $4200 * 1.25 emergency multiplier = $5250.00
        surgeon_item = next(i for i in items if i.item_code.startswith("SURGEON_FEE_"))
        self.assertEqual(surgeon_item.total_amount, 5250.00)

        # OT rate $550 * 1.25 = $687.50 * 4.0 hrs = $2750.00
        ot_item = next(i for i in items if i.item_code.startswith("OT_RENT_"))
        self.assertEqual(ot_item.total_amount, 2750.00)


if __name__ == "__main__":
    unittest.main()

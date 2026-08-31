"""
MedBill Enterprise - Automated Test Suite 2: Hospital Bed & Room Tariff Calculation
Validates multi-day inpatient stays, room category transfers, midnight census calculations,
and metered medical gas / ventilator billing.
"""

import unittest
from datetime import datetime, timedelta
import uuid

from medbill.core.models import (
    Encounter,
    EncounterType,
    RoomCategoryType,
    BillingItemCategory,
)
from medbill.modules.bed_management.room_tariff_calculator import (
    RoomBedTariffCalculator,
    RoomStayPeriod,
)
from medbill.catalogs.room_categories import ROOM_TARIFF_CATALOG


class TestRoomBedTariffCalculation(unittest.TestCase):

    def setUp(self):
        self.calculator = RoomBedTariffCalculator()

    def test_multi_day_private_deluxe_stay(self):
        """Test a 3-day stay in Private Deluxe room with nursing and resident care."""
        start_time = datetime(2026, 9, 1, 14, 0, 0)
        end_time = datetime(2026, 9, 4, 11, 0, 0)  # 3 midnights crossed (Sep 1->2, 2->3, 3->4)

        encounter = Encounter(
            encounter_id="ENC_IPD_001",
            patient_id="PAT_2001",
            encounter_type=EncounterType.INPATIENT,
            admission_time=start_time,
            discharge_time=end_time,
            room_category=RoomCategoryType.PRIVATE_DELUXE
        )

        period = RoomStayPeriod(
            category=RoomCategoryType.PRIVATE_DELUXE,
            start_time=start_time,
            end_time=end_time
        )

        items = self.calculator.calculate_stay_charges(encounter, [period])

        # Verify line items generated
        categories = [item.category for item in items]
        self.assertIn(BillingItemCategory.ROOM_BED, categories)
        self.assertIn(BillingItemCategory.NURSING, categories)
        self.assertIn(BillingItemCategory.CONSULTATION, categories)
        self.assertIn(BillingItemCategory.MISCELLANEOUS, categories)

        room_item = next(item for item in items if item.category == BillingItemCategory.ROOM_BED)
        # 3 days @ $1450/day = $4350.00
        self.assertEqual(room_item.quantity, 3.0)
        self.assertEqual(room_item.unit_price, 1450.00)
        self.assertEqual(room_item.total_amount, 4350.00)

        nursing_item = next(item for item in items if item.category == BillingItemCategory.NURSING)
        # 3 days @ $260/day = $780.00
        self.assertEqual(nursing_item.total_amount, 780.00)

    def test_icu_stay_with_metered_oxygen_and_ventilator(self):
        """Test ICU admission with 24 hours of mechanical ventilation and continuous oxygen."""
        start_time = datetime(2026, 9, 1, 8, 0, 0)
        end_time = datetime(2026, 9, 3, 8, 0, 0)  # 2 full days in ICU

        encounter = Encounter(
            encounter_id="ENC_ICU_001",
            patient_id="PAT_2002",
            encounter_type=EncounterType.INPATIENT,
            admission_time=start_time,
            discharge_time=end_time,
            room_category=RoomCategoryType.INTENSIVE_CARE_UNIT_ICU
        )

        period = RoomStayPeriod(
            category=RoomCategoryType.INTENSIVE_CARE_UNIT_ICU,
            start_time=start_time,
            end_time=end_time,
            metered_oxygen_hours=36.0,
            ventilator_hours=24.0,
            telemetry_hours=48.0,
            infusion_pump_days=2.0
        )

        items = self.calculator.calculate_stay_charges(encounter, [period])

        # ICU Base: 2 days @ 3200 = 6400
        room_item = next(item for item in items if item.category == BillingItemCategory.ROOM_BED)
        self.assertEqual(room_item.total_amount, 6400.00)

        # Oxygen: 36 hrs @ $35.00/hr = $1260.00
        o2_item = next(item for item in items if item.category == BillingItemCategory.MEDICAL_GAS)
        self.assertEqual(o2_item.quantity, 36.0)
        self.assertEqual(o2_item.unit_price, 35.00)
        self.assertEqual(o2_item.total_amount, 1260.00)

        # Ventilator: 24 hrs @ $125.00/hr = $3000.00
        vent_item = next(item for item in items if item.item_code == "EQUIP_VENTILATOR")
        self.assertEqual(vent_item.quantity, 24.0)
        self.assertEqual(vent_item.unit_price, 125.00)
        self.assertEqual(vent_item.total_amount, 3000.00)

        # Telemetry: 48 hrs @ $50.00/hr = $2400.00
        telem_item = next(item for item in items if item.item_code == "EQUIP_TELEMETRY")
        self.assertEqual(telem_item.quantity, 48.0)
        self.assertEqual(telem_item.total_amount, 2400.00)

    def test_room_transfer_icu_to_general_ward(self):
        """Test patient transitioning from ICU (1 day) to General Ward (2 days)."""
        icu_start = datetime(2026, 9, 1, 10, 0, 0)
        icu_end = datetime(2026, 9, 2, 10, 0, 0)  # 1 day ICU
        ward_end = datetime(2026, 9, 4, 10, 0, 0)  # 2 days General Ward

        encounter = Encounter(
            encounter_id="ENC_IPD_002",
            patient_id="PAT_2003",
            encounter_type=EncounterType.INPATIENT,
            admission_time=icu_start,
            discharge_time=ward_end
        )

        period_icu = RoomStayPeriod(
            category=RoomCategoryType.INTENSIVE_CARE_UNIT_ICU,
            start_time=icu_start,
            end_time=icu_end
        )
        period_ward = RoomStayPeriod(
            category=RoomCategoryType.GENERAL_WARD_MALE,
            start_time=icu_end,
            end_time=ward_end
        )

        items = self.calculator.calculate_stay_charges(encounter, [period_icu, period_ward])

        room_items = [item for item in items if item.category == BillingItemCategory.ROOM_BED]
        self.assertEqual(len(room_items), 2)
        # ICU room charge: 1 day @ 3200 = 3200
        self.assertEqual(room_items[0].total_amount, 3200.00)
        # Ward room charge: 2 days @ 450 = 900
        self.assertEqual(room_items[1].total_amount, 900.00)


if __name__ == "__main__":
    unittest.main()

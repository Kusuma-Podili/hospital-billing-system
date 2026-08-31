"""
MedBill Enterprise - Tariff Master Service
Manages dynamic hospital fee schedules, institutional tariff revisions,
government scheme price caps, and service pricing lookups.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from medbill.core.models import BillingItemCategory
from medbill.catalogs.cpt_codes import CPT_CATALOG, CPTCodeEntry
from medbill.catalogs.doctors_specialties import SPECIALTY_CATALOG, SpecialtyTariffSchedule
from medbill.catalogs.room_categories import ROOM_TARIFF_CATALOG, RoomTariffSchedule


class TariffMasterService:
    """
    Centralized service for hospital fee schedule administration and dynamic price resolving.
    """

    def __init__(self):
        self.cpt_catalog = CPT_CATALOG
        self.specialty_catalog = SPECIALTY_CATALOG
        self.room_catalog = ROOM_TARIFF_CATALOG
        self.custom_tariff_overrides: Dict[str, float] = {}
        self.scheme_discount_caps: Dict[str, float] = {
            "AYUSHMAN_BHARAT": 40.0,  # 40% discount cap
            "MEDICARE_ADVANTAGE": 25.0,
            "MEDICAID_STANDARD": 35.0,
            "SENIOR_CITIZEN": 15.0,
            "HOSPITAL_EMPLOYEE": 50.0,
        }

    def set_tariff_override(self, item_code: str, custom_fee: float) -> None:
        """Override standard tariff for specific service code."""
        self.custom_tariff_overrides[item_code] = custom_fee

    def get_service_price(self, item_code: str, default_price: float = 0.0) -> float:
        """Get the active price for an item code."""
        if item_code in self.custom_tariff_overrides:
            return self.custom_tariff_overrides[item_code]
        if item_code in self.cpt_catalog:
            return self.cpt_catalog[item_code].standard_fee
        return default_price

    def get_scheme_discount_percent(self, scheme_code: str) -> float:
        """Retrieve discount percentage for a government or corporate scheme."""
        return self.scheme_discount_caps.get(scheme_code.upper(), 0.0)

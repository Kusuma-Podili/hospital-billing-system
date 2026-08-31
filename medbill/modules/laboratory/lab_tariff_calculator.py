"""
MedBill Enterprise - Diagnostic Laboratory & Radiology Tariff Calculator
Calculates diagnostic panel pricing, specimen handling, urgent STAT multipliers,
pathologist/radiologist interpretation fees, and bundled wellness package discounts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid

from medbill.core.models import (
    Encounter,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.catalogs.loinc_lab_panels import (
    LOINC_LAB_CATALOG,
    LabPanelEntry,
    get_lab_panel,
)


@dataclass
class DiagnosticOrder:
    loinc_code: str
    is_stat_urgent: bool = False
    ordering_doctor_id: Optional[str] = None
    home_collection_requested: bool = False
    discount_percent: float = 0.0


class LabTariffCalculator:
    """
    Enterprise laboratory and radiology diagnostic billing engine.
    """

    HOME_COLLECTION_FEE = 25.00
    MULTI_PANEL_BUNDLE_THRESHOLD = 3
    MULTI_PANEL_BUNDLE_DISCOUNT_PERCENT = 10.0  # 10% bundle discount for 3+ lab orders

    def __init__(self, loinc_catalog: Optional[Dict[str, LabPanelEntry]] = None):
        self.loinc_catalog = loinc_catalog or LOINC_LAB_CATALOG

    def calculate_diagnostic_orders(
        self,
        encounter: Encounter,
        orders: List[DiagnosticOrder]
    ) -> List[BillingLineItem]:
        """
        Calculates diagnostic billing items including specimen handling, STAT multipliers, and pathologist reviews.
        """
        line_items: List[BillingLineItem] = []
        apply_bundle_discount = len(orders) >= self.MULTI_PANEL_BUNDLE_THRESHOLD

        for order in orders:
            panel = self.loinc_catalog.get(order.loinc_code)
            if not panel:
                continue

            # Determine Category: Radiology vs Laboratory
            category = BillingItemCategory.RADIOLOGY if panel.department == "Radiology" else BillingItemCategory.LABORATORY

            # Base test price + STAT multiplier
            unit_price = panel.standard_price
            if order.is_stat_urgent:
                unit_price = round(unit_price * panel.urgent_stat_multiplier, 2)

            # Combined discount: order specific or multi-panel bundle
            total_discount_pct = order.discount_percent
            if apply_bundle_discount and total_discount_pct == 0.0:
                total_discount_pct = self.MULTI_PANEL_BUNDLE_DISCOUNT_PERCENT

            discount_amt = round(unit_price * (total_discount_pct / 100.0), 2)
            final_test_charge = unit_price - discount_amt

            desc = f"{panel.panel_name} (LOINC: {panel.loinc_code} / CPT: {panel.cpt_equivalent}) - Specimen: {panel.specimen_type}."
            if order.is_stat_urgent:
                desc += " [URGENT STAT PRIORITY]."

            test_item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=category,
                item_code=panel.loinc_code,
                item_name=panel.panel_name,
                description=desc,
                unit_price=unit_price,
                quantity=1.0,
                subtotal=unit_price,
                discount_amount=discount_amt,
                tax_rate_percent=0.0,  # Diagnostic tests 0% exempt
                total_amount=final_test_charge,
                performed_by_id=order.ordering_doctor_id,
                metadata={
                    "loinc": panel.loinc_code,
                    "cpt": panel.cpt_equivalent,
                    "department": panel.department,
                    "is_stat": order.is_stat_urgent,
                    "subtests": panel.included_subtests
                }
            )
            line_items.append(test_item)

            # Phlebotomy / Specimen Handling Fee (if applicable and non-zero)
            if panel.specimen_collection_fee > 0:
                spec_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.LABORATORY,
                    item_code="PHLEBOTOMY_FEE",
                    item_name="Phlebotomy & Specimen Transport Handling",
                    description=f"Aseptic vacuum blood/specimen collection for {panel.panel_name}",
                    unit_price=panel.specimen_collection_fee,
                    quantity=1.0,
                    subtotal=panel.specimen_collection_fee,
                    tax_rate_percent=0.0,
                    total_amount=panel.specimen_collection_fee
                )
                line_items.append(spec_item)

            # Professional Pathologist / Radiologist Reading & Report Fee
            if panel.professional_review_fee > 0:
                prof_name = "Radiologist Diagnostic Imaging Report" if panel.department == "Radiology" else "Consultant Pathologist Verification & Report"
                prof_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=category,
                    item_code=f"PROF_READ_{panel.loinc_code}",
                    item_name=prof_name,
                    description=f"Specialist diagnostic review for {panel.panel_name}",
                    unit_price=panel.professional_review_fee,
                    quantity=1.0,
                    subtotal=panel.professional_review_fee,
                    tax_rate_percent=0.0,
                    total_amount=panel.professional_review_fee
                )
                line_items.append(prof_item)

            # Home Sample Collection Fee (if requested)
            if order.home_collection_requested:
                home_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.MISCELLANEOUS,
                    item_code="HOME_SAMPLE_COLLECTION",
                    item_name="Home Phlebotomy & Sample Cold-Chain Transport",
                    description="Doorstep diagnostic specimen collection",
                    unit_price=self.HOME_COLLECTION_FEE,
                    quantity=1.0,
                    subtotal=self.HOME_COLLECTION_FEE,
                    tax_rate_percent=0.0,
                    total_amount=self.HOME_COLLECTION_FEE
                )
                line_items.append(home_item)

        return line_items

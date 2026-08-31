"""
MedBill Enterprise - Hospital Pharmacy & Medication Dispensing Calculator
Calculates drug prices, batch lot tracking, prescription tax rates, compounding fees,
and controlled substance regulatory audit entries.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Dict, Optional, Any
import uuid

from medbill.core.models import (
    Encounter,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.catalogs.pharmacy_ndc import (
    PHARMACY_NDC_CATALOG,
    MedicationEntry,
    get_medication_entry,
)


@dataclass
class PrescriptionOrder:
    ndc: str
    quantity: float
    batch_number: str
    expiry_date: str  # YYYY-MM-DD
    prescribed_by_doctor_id: str
    is_stat_urgent: bool = False
    is_compounded_iv: bool = False  # If compounding / sterile IV admixture required
    custom_dosage_instructions: str = ""
    discount_percent: float = 0.0


class PharmacyTariffCalculator:
    """
    Enterprise pharmacy dispensing and revenue cycle calculator.
    """

    BASE_DISPENSING_FEE = 3.50  # Standard pharmacist dispensing & verification fee
    IV_COMPOUNDING_FEE = 15.00  # Cleanroom sterile preparation fee
    STAT_URGENT_PHARMACY_FEE = 10.00  # Rapid bedside tube delivery fee

    def __init__(self, ndc_catalog: Optional[Dict[str, MedicationEntry]] = None):
        self.ndc_catalog = ndc_catalog or PHARMACY_NDC_CATALOG

    def is_batch_expired(self, expiry_date_str: str) -> bool:
        """Check if medication batch has passed expiration date."""
        try:
            exp = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            return exp < date.today()
        except Exception:
            return False

    def dispense_medications(
        self,
        encounter: Encounter,
        orders: List[PrescriptionOrder]
    ) -> List[BillingLineItem]:
        """
        Processes prescription orders into itemized billing lines with tax, batch tracking, and dispensing fees.
        """
        line_items: List[BillingLineItem] = []

        for order in orders:
            med = self.ndc_catalog.get(order.ndc)
            if not med:
                continue

            if self.is_batch_expired(order.expiry_date):
                raise ValueError(f"CRITICAL SAFETY WARNING: Cannot dispense expired batch {order.batch_number} for NDC {order.ndc} (Expired on {order.expiry_date})")

            # Calculate base drug price
            unit_price = med.unit_selling_price
            raw_subtotal = round(unit_price * order.quantity, 2)

            # Apply order discount
            discount_amount = round(raw_subtotal * (order.discount_percent / 100.0), 2)
            after_discount = raw_subtotal - discount_amount

            # Calculate Dispensing Tax
            tax_rate = med.dispensing_tax_percent
            tax_amount = round(after_discount * (tax_rate / 100.0), 2)
            total = round(after_discount + tax_amount, 2)

            desc = f"{med.generic_name} ({med.strength}, {med.dosage_form}) - Lot: {order.batch_number} (Exp: {order.expiry_date})"
            if order.custom_dosage_instructions:
                desc += f" | Sig: {order.custom_dosage_instructions}"

            item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=BillingItemCategory.PHARMACY,
                item_code=med.ndc,
                item_name=f"{med.brand_name} {med.strength}",
                description=desc,
                unit_price=unit_price,
                quantity=order.quantity,
                subtotal=raw_subtotal,
                discount_amount=discount_amount,
                tax_rate_percent=tax_rate,
                tax_amount=tax_amount,
                total_amount=total,
                performed_by_id=order.prescribed_by_doctor_id,
                metadata={
                    "ndc": med.ndc,
                    "rxnorm_cui": med.rxnorm_cui,
                    "batch_number": order.batch_number,
                    "expiry_date": order.expiry_date,
                    "is_controlled": med.is_controlled_substance,
                    "dea_schedule": med.dea_schedule,
                    "is_high_alert": med.is_high_alert,
                    "is_compounded": order.is_compounded_iv
                }
            )
            line_items.append(item)

            # Add sterile IV compounding fee if applicable
            if order.is_compounded_iv:
                comp_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.PHARMACY,
                    item_code="PHARM_COMPOUNDING",
                    item_name="Sterile IV Admixture & Compounding Service",
                    description=f"Aseptic cleanroom preparation for {med.brand_name} {med.strength}",
                    unit_price=self.IV_COMPOUNDING_FEE,
                    quantity=1.0,
                    subtotal=self.IV_COMPOUNDING_FEE,
                    tax_rate_percent=0.0,
                    total_amount=self.IV_COMPOUNDING_FEE
                )
                line_items.append(comp_item)

            # Add STAT emergency delivery fee if urgent
            if order.is_stat_urgent:
                stat_item = BillingLineItem(
                    item_id=str(uuid.uuid4()),
                    encounter_id=encounter.encounter_id,
                    category=BillingItemCategory.PHARMACY,
                    item_code="PHARM_STAT_DELIVERY",
                    item_name="Urgent STAT Pharmacy Bedside Dispensing",
                    description="Priority emergency pharmacy order delivery",
                    unit_price=self.STAT_URGENT_PHARMACY_FEE,
                    quantity=1.0,
                    subtotal=self.STAT_URGENT_PHARMACY_FEE,
                    tax_rate_percent=0.0,
                    total_amount=self.STAT_URGENT_PHARMACY_FEE
                )
                line_items.append(stat_item)

        return line_items

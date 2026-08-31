"""
MedBill Enterprise - Surgical Procedure & Operating Theater (OT) Costing Calculator
Calculates total surgical episode costs including OT table time, Chief Surgeon fees,
Assistant Surgeons, Anesthesiologist tariffs, surgical consumable kits, implants, and PACU recovery stay.
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
from medbill.catalogs.surgical_packages import (
    SURGERY_CATALOG,
    SurgicalProcedurePackage,
    get_surgical_package,
)


@dataclass
class SurgeryExecutionDetails:
    procedure_code: str
    actual_duration_hours: float
    chief_surgeon_id: str
    anesthesiologist_id: str
    co_surgeon_id: Optional[str] = None
    actual_implant_cost: Optional[float] = None
    implant_serial_number: Optional[str] = None
    pacu_recovery_hours: float = 2.0
    extra_consumables_fee: float = 0.0
    is_emergency_surgery: bool = False


class SurgicalCostingCalculator:
    """
    Enterprise calculator for surgical procedures and operating theatre packages.
    """

    EMERGENCY_SURGERY_SURCHARGE_PERCENT = 25.0  # +25% for emergency out-of-hours surgery

    def __init__(self, surgery_catalog: Optional[Dict[str, SurgicalProcedurePackage]] = None):
        self.surgery_catalog = surgery_catalog or SURGERY_CATALOG

    def calculate_surgical_episode(
        self,
        encounter: Encounter,
        surgery: SurgeryExecutionDetails
    ) -> List[BillingLineItem]:
        """
        Generates full itemized billing lines for a surgical procedure.
        """
        pkg = self.surgery_catalog.get(surgery.procedure_code)
        if not pkg:
            raise ValueError(f"Surgical procedure with CPT code {surgery.procedure_code} not found in catalog")

        line_items: List[BillingLineItem] = []
        emergency_mult = 1.25 if surgery.is_emergency_surgery else 1.0

        # 1. Operating Theater Table Time & Staff Charge
        ot_table_rate = pkg.ot_table_hourly_rate * emergency_mult
        ot_duration = max(0.5, surgery.actual_duration_hours)
        ot_total = round(ot_table_rate * ot_duration, 2)

        ot_item = BillingLineItem(
            item_id=str(uuid.uuid4()),
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.SURGERY,
            item_code=f"OT_RENT_{pkg.procedure_code}",
            item_name=f"Operating Theater Utilization ({pkg.surgical_tier})",
            description=f"OT time for {pkg.procedure_name} ({ot_duration:.1f} hrs @ ${ot_table_rate:.2f}/hr)" +
                        (" [EMERGENCY OT SURCHARGE]" if surgery.is_emergency_surgery else ""),
            unit_price=ot_table_rate,
            quantity=ot_duration,
            subtotal=ot_total,
            tax_rate_percent=0.0,
            total_amount=ot_total,
            metadata={
                "surgical_tier": pkg.surgical_tier,
                "duration_hours": ot_duration,
                "is_emergency": surgery.is_emergency_surgery
            }
        )
        line_items.append(ot_item)

        # 2. Chief Surgeon Professional Fee
        surgeon_fee = round(pkg.chief_surgeon_base_fee * emergency_mult, 2)
        surgeon_item = BillingLineItem(
            item_id=str(uuid.uuid4()),
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.SURGERY,
            item_code=f"SURGEON_FEE_{pkg.procedure_code}",
            item_name=f"Chief Operating Surgeon Fee - {pkg.procedure_name}",
            description=f"Primary surgical intervention and operative procedure ({pkg.surgical_tier} tier)",
            unit_price=surgeon_fee,
            quantity=1.0,
            subtotal=surgeon_fee,
            tax_rate_percent=0.0,
            total_amount=surgeon_fee,
            performed_by_id=surgery.chief_surgeon_id
        )
        line_items.append(surgeon_item)

        # 3. Co-Surgeon / Assistant Surgeon Fee (if assigned)
        if surgery.co_surgeon_id and pkg.co_surgeon_fee > 0:
            co_fee = round(pkg.co_surgeon_fee * emergency_mult, 2)
            co_item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=BillingItemCategory.SURGERY,
                item_code=f"CO_SURGEON_{pkg.procedure_code}",
                item_name="Assistant / Co-Surgeon Professional Fee",
                description=f"Assisting primary surgeon in {pkg.procedure_name}",
                unit_price=co_fee,
                quantity=1.0,
                subtotal=co_fee,
                tax_rate_percent=0.0,
                total_amount=co_fee,
                performed_by_id=surgery.co_surgeon_id
            )
            line_items.append(co_item)

        # 4. Anesthesiologist Professional Fee
        anesthesia_fee = round(pkg.anesthesiologist_fee * emergency_mult, 2)
        anesthesia_item = BillingLineItem(
            item_id=str(uuid.uuid4()),
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.ANESTHESIA,
            item_code=f"ANESTHESIA_{pkg.procedure_code}",
            item_name="Consultant Anesthesiologist Fee & Intraoperative Monitoring",
            description=f"General/Regional anesthesia and hemodynamic stability maintenance",
            unit_price=anesthesia_fee,
            quantity=1.0,
            subtotal=anesthesia_fee,
            tax_rate_percent=0.0,
            total_amount=anesthesia_fee,
            performed_by_id=surgery.anesthesiologist_id
        )
        line_items.append(anesthesia_item)

        # 5. Standard Surgical Consumable Kit & Drapes
        total_consumables = pkg.standard_consumables_fee + surgery.extra_consumables_fee
        consumable_item = BillingLineItem(
            item_id=str(uuid.uuid4()),
            encounter_id=encounter.encounter_id,
            category=BillingItemCategory.SURGERY,
            item_code=f"SURG_KIT_{pkg.procedure_code}",
            item_name=f"Sterile Surgical Consumables & Disposable Pack",
            description=f"Aseptic gowns, drapes, suction tubing, cautery tips, sutures and laparoscopy disposables",
            unit_price=total_consumables,
            quantity=1.0,
            subtotal=total_consumables,
            tax_rate_percent=0.0,
            total_amount=total_consumables
        )
        line_items.append(consumable_item)

        # 6. Surgical Implants / Prostheses (e.g. Knee, Hip, Mesh, IOL, Screws)
        implant_cost = surgery.actual_implant_cost if surgery.actual_implant_cost is not None else pkg.estimated_implant_cost
        if implant_cost > 0:
            implant_desc = f"Medical implant for {pkg.procedure_name}"
            if surgery.implant_serial_number:
                implant_desc += f" (Serial/Lot #{surgery.implant_serial_number})"
            implant_item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=BillingItemCategory.SURGERY,
                item_code=f"IMPLANT_{pkg.procedure_code}",
                item_name=f"Surgical Implant / Prosthetic Device",
                description=implant_desc,
                unit_price=implant_cost,
                quantity=1.0,
                subtotal=implant_cost,
                tax_rate_percent=5.0,  # 5% medical device tax
                metadata={"serial_number": surgery.implant_serial_number}
            )
            implant_item.calculate_totals()
            line_items.append(implant_item)

        # 7. PACU / Post-Anesthesia Recovery Room Stay
        if surgery.pacu_recovery_hours > 0:
            pacu_rate = pkg.recovery_pacu_hourly_rate
            pacu_total = round(pacu_rate * surgery.pacu_recovery_hours, 2)
            pacu_item = BillingLineItem(
                item_id=str(uuid.uuid4()),
                encounter_id=encounter.encounter_id,
                category=BillingItemCategory.ROOM_BED,
                item_code="PACU_RECOVERY",
                item_name="Post-Anesthesia Care Unit (PACU) Stay",
                description=f"Post-operative recovery monitoring ({surgery.pacu_recovery_hours:.1f} hrs @ ${pacu_rate:.2f}/hr)",
                unit_price=pacu_rate,
                quantity=surgery.pacu_recovery_hours,
                subtotal=pacu_total,
                tax_rate_percent=0.0,
                total_amount=pacu_total
            )
            line_items.append(pacu_item)

        return line_items

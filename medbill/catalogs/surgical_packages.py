"""
MedBill Enterprise Catalogs - Surgical Packages & Operating Theater (OT) Catalog
Defines comprehensive surgical procedures, OT table hourly tiers, Chief Surgeon & Anesthetist fees,
consumable packs, implants, and Post-Anesthesia Care Unit (PACU) tariffs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class SurgicalProcedurePackage:
    procedure_code: str  # CPT code
    procedure_name: str
    surgical_tier: str  # Minor, Major, Supra-Major, Complex/Tertiary
    department: str
    standard_duration_hours: float
    ot_table_hourly_rate: float
    chief_surgeon_base_fee: float
    co_surgeon_fee: float
    anesthesiologist_fee: float
    standard_consumables_fee: float
    recovery_pacu_hourly_rate: float
    estimated_implant_cost: float = 0.0
    global_period_days: int = 90
    required_staff: List[str] = field(default_factory=lambda: ["Scrub Nurse", "Circulating Nurse", "OT Technician"])


# Exhaustive Surgical Procedure Catalog
SURGERY_CATALOG: Dict[str, SurgicalProcedurePackage] = {
    "47562": SurgicalProcedurePackage(
        procedure_code="47562",
        procedure_name="Laparoscopic Cholecystectomy (Gallbladder Removal)",
        surgical_tier="Major",
        department="General Surgery",
        standard_duration_hours=2.0,
        ot_table_hourly_rate=350.00,
        chief_surgeon_base_fee=1800.00,
        co_surgeon_fee=450.00,
        anesthesiologist_fee=650.00,
        standard_consumables_fee=550.00,
        recovery_pacu_hourly_rate=80.00
    ),
    "44970": SurgicalProcedurePackage(
        procedure_code="44970",
        procedure_name="Laparoscopic Appendectomy",
        surgical_tier="Major",
        department="General Surgery",
        standard_duration_hours=1.5,
        ot_table_hourly_rate=350.00,
        chief_surgeon_base_fee=1500.00,
        co_surgeon_fee=380.00,
        anesthesiologist_fee=550.00,
        standard_consumables_fee=480.00,
        recovery_pacu_hourly_rate=80.00
    ),
    "27447": SurgicalProcedurePackage(
        procedure_code="27447",
        procedure_name="Total Knee Arthroplasty (TKR - Unilateral)",
        surgical_tier="Supra-Major",
        department="Orthopedics",
        standard_duration_hours=3.0,
        ot_table_hourly_rate=450.00,
        chief_surgeon_base_fee=2800.00,
        co_surgeon_fee=700.00,
        anesthesiologist_fee=850.00,
        standard_consumables_fee=950.00,
        recovery_pacu_hourly_rate=110.00,
        estimated_implant_cost=3200.00  # High-grade titanium/cobalt knee prosthesis
    ),
    "27130": SurgicalProcedurePackage(
        procedure_code="27130",
        procedure_name="Total Hip Replacement (THR - Unilateral)",
        surgical_tier="Supra-Major",
        department="Orthopedics",
        standard_duration_hours=3.5,
        ot_table_hourly_rate=450.00,
        chief_surgeon_base_fee=3000.00,
        co_surgeon_fee=750.00,
        anesthesiologist_fee=900.00,
        standard_consumables_fee=1050.00,
        recovery_pacu_hourly_rate=110.00,
        estimated_implant_cost=3500.00  # Ceramic/titanium acetabular & femoral system
    ),
    "33533": SurgicalProcedurePackage(
        procedure_code="33533",
        procedure_name="Coronary Artery Bypass Graft (CABG x3 on CPB Pump)",
        surgical_tier="Complex/Tertiary",
        department="Cardiothoracic Surgery",
        standard_duration_hours=5.5,
        ot_table_hourly_rate=650.00,
        chief_surgeon_base_fee=4800.00,
        co_surgeon_fee=1400.00,
        anesthesiologist_fee=1500.00,
        standard_consumables_fee=2200.00,
        recovery_pacu_hourly_rate=150.00,
        estimated_implant_cost=1800.00  # Heart-lung machine circuit, cannulas, sternal wires
    ),
    "61154": SurgicalProcedurePackage(
        procedure_code="61154",
        procedure_name="Emergency Craniotomy for Subdural / Epidural Hematoma Evacuation",
        surgical_tier="Complex/Tertiary",
        department="Neurosurgery",
        standard_duration_hours=4.0,
        ot_table_hourly_rate=550.00,
        chief_surgeon_base_fee=4200.00,
        co_surgeon_fee=1100.00,
        anesthesiologist_fee=1200.00,
        standard_consumables_fee=1600.00,
        recovery_pacu_hourly_rate=140.00,
        estimated_implant_cost=950.00  # Cranial fixation plates & titanium screws
    ),
    "66984": SurgicalProcedurePackage(
        procedure_code="66984",
        procedure_name="Cataract Phacoemulsification with Foldable IOL Implantation",
        surgical_tier="Minor / Daycare",
        department="Ophthalmology",
        standard_duration_hours=0.75,
        ot_table_hourly_rate=250.00,
        chief_surgeon_base_fee=950.00,
        co_surgeon_fee=0.00,
        anesthesiologist_fee=250.00,
        standard_consumables_fee=220.00,
        recovery_pacu_hourly_rate=50.00,
        estimated_implant_cost=450.00  # Hydrophobic acrylic intraocular lens
    ),
    "49505": SurgicalProcedurePackage(
        procedure_code="49505",
        procedure_name="Open Inguinal Hernia Mesh Hernioplasty",
        surgical_tier="Major",
        department="General Surgery",
        standard_duration_hours=1.5,
        ot_table_hourly_rate=350.00,
        chief_surgeon_base_fee=1250.00,
        co_surgeon_fee=300.00,
        anesthesiologist_fee=450.00,
        standard_consumables_fee=380.00,
        recovery_pacu_hourly_rate=80.00,
        estimated_implant_cost=250.00  # Polypropylene prosthetic mesh
    )
}


def get_surgical_package(procedure_code: str) -> Optional[SurgicalProcedurePackage]:
    """Retrieve surgical package by procedure CPT code."""
    return SURGERY_CATALOG.get(procedure_code)


def search_surgeries(query: str, limit: int = 15) -> List[SurgicalProcedurePackage]:
    """Search surgical catalog by name, code, or department."""
    q = query.lower()
    matches = [
        pkg for pkg in SURGERY_CATALOG.values()
        if q in pkg.procedure_name.lower() or q in pkg.procedure_code or q in pkg.department.lower()
    ]
    return matches[:limit]

"""
MedBill Enterprise Catalogs - Pharmacy NDC & RxNorm Master Medication Catalog
Defines comprehensive pharmaceutical drugs, National Drug Codes (NDC), dosage forms,
strength, unit hospital prices, dispensing tax rates, and scheduled drug classifications.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class MedicationEntry:
    ndc: str
    brand_name: str
    generic_name: str
    rxnorm_cui: str
    category: str
    dosage_form: str  # Tablet, Capsule, Vial, Ampoule, Infusion, Syrup, Pre-filled Syringe
    strength: str
    unit_cost: float  # Hospital acquisition cost
    unit_selling_price: float  # Base charge before dispensing fees & tax
    dispensing_tax_percent: float  # 0%, 5%, 12%, 18%
    is_controlled_substance: bool = False
    dea_schedule: Optional[str] = None  # Schedule II, III, IV, V
    is_high_alert: bool = False  # Chemo, concentrated electrolytes, insulin, heparin
    requires_refrigeration: bool = False
    manufacturer: str = "MedPharma Global"


# Exhaustive NDC Medication Catalog
PHARMACY_NDC_CATALOG: Dict[str, MedicationEntry] = {
    # --- Antibiotics & Anti-Infectives ---
    "00093-3147-01": MedicationEntry(
        ndc="00093-3147-01",
        brand_name="Augmentin",
        generic_name="Amoxicillin and Clavulanate Potassium",
        rxnorm_cui="225658",
        category="Antibiotic",
        dosage_form="Tablet",
        strength="875mg / 125mg",
        unit_cost=1.20,
        unit_selling_price=4.50,
        dispensing_tax_percent=5.0
    ),
    "00004-0800-85": MedicationEntry(
        ndc="00004-0800-85",
        brand_name="Rocephin",
        generic_name="Ceftriaxone Sodium",
        rxnorm_cui="309090",
        category="Antibiotic (Cephalosporin)",
        dosage_form="Vial (IV/IM)",
        strength="1000mg (1g)",
        unit_cost=4.80,
        unit_selling_price=18.50,
        dispensing_tax_percent=5.0
    ),
    "00074-6332-11": MedicationEntry(
        ndc="00074-6332-11",
        brand_name="Vancocin",
        generic_name="Vancomycin Hydrochloride",
        rxnorm_cui="313586",
        category="Antibiotic (Glycopeptide)",
        dosage_form="Vial (IV Infusion)",
        strength="1g (1000mg)",
        unit_cost=8.50,
        unit_selling_price=32.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),
    "00024-5850-10": MedicationEntry(
        ndc="00024-5850-10",
        brand_name="Merrem",
        generic_name="Meropenem",
        rxnorm_cui="311746",
        category="Antibiotic (Carbapenem)",
        dosage_form="Vial (IV)",
        strength="1g",
        unit_cost=14.00,
        unit_selling_price=48.00,
        dispensing_tax_percent=5.0
    ),
    "00009-0395-02": MedicationEntry(
        ndc="00009-0395-02",
        brand_name="Cleocin",
        generic_name="Clindamycin Phosphate",
        rxnorm_cui="309256",
        category="Antibiotic (Lincosamide)",
        dosage_form="Vial (IV)",
        strength="600mg / 4mL",
        unit_cost=3.10,
        unit_selling_price=12.50,
        dispensing_tax_percent=5.0
    ),
    "00085-0566-05": MedicationEntry(
        ndc="00085-0566-05",
        brand_name="Avelox",
        generic_name="Moxifloxacin Hydrochloride",
        rxnorm_cui="311867",
        category="Antibiotic (Fluoroquinolone)",
        dosage_form="IV Infusion Bag",
        strength="400mg / 250mL",
        unit_cost=9.20,
        unit_selling_price=35.00,
        dispensing_tax_percent=5.0
    ),

    # --- Analgesics, Opioids & Anti-Inflammatories ---
    "00045-0255-10": MedicationEntry(
        ndc="00045-0255-10",
        brand_name="Sublimaze",
        generic_name="Fentanyl Citrate",
        rxnorm_cui="310287",
        category="Analgesic (Opioid)",
        dosage_form="Ampoule (IV)",
        strength="100mcg / 2mL",
        unit_cost=2.20,
        unit_selling_price=15.00,
        dispensing_tax_percent=0.0,
        is_controlled_substance=True,
        dea_schedule="Schedule II",
        is_high_alert=True
    ),
    "00641-6071-10": MedicationEntry(
        ndc="00641-6071-10",
        brand_name="Duramorph",
        generic_name="Morphine Sulfate",
        rxnorm_cui="311995",
        category="Analgesic (Opioid)",
        dosage_form="Ampoule (IV)",
        strength="10mg / 1mL",
        unit_cost=1.80,
        unit_selling_price=14.00,
        dispensing_tax_percent=0.0,
        is_controlled_substance=True,
        dea_schedule="Schedule II",
        is_high_alert=True
    ),
    "00004-0038-22": MedicationEntry(
        ndc="00004-0038-22",
        brand_name="Toradol",
        generic_name="Ketorolac Tromethamine",
        rxnorm_cui="311354",
        category="NSAID Analgesic",
        dosage_form="Vial (IV/IM)",
        strength="30mg / 1mL",
        unit_cost=1.50,
        unit_selling_price=8.50,
        dispensing_tax_percent=5.0
    ),
    "00007-3230-20": MedicationEntry(
        ndc="00007-3230-20",
        brand_name="Ofirmev",
        generic_name="Acetaminophen (Paracetamol)",
        rxnorm_cui="313798",
        category="Antipyretic / Analgesic",
        dosage_form="IV Infusion Vial",
        strength="1000mg / 100mL",
        unit_cost=3.50,
        unit_selling_price=16.00,
        dispensing_tax_percent=5.0
    ),

    # --- Cardiovascular & Anticoagulants ---
    "00002-7510-01": MedicationEntry(
        ndc="00002-7510-01",
        brand_name="Lovenox",
        generic_name="Enoxaparin Sodium",
        rxnorm_cui="310149",
        category="Anticoagulant (LMWH)",
        dosage_form="Pre-filled Syringe",
        strength="40mg / 0.4mL",
        unit_cost=6.50,
        unit_selling_price=28.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),
    "00069-3150-83": MedicationEntry(
        ndc="00069-3150-83",
        brand_name="Norvasc",
        generic_name="Amlodipine Besylate",
        rxnorm_cui="308136",
        category="Antihypertensive (CCB)",
        dosage_form="Tablet",
        strength="5mg",
        unit_cost=0.15,
        unit_selling_price=1.20,
        dispensing_tax_percent=5.0
    ),
    "00071-0155-23": MedicationEntry(
        ndc="00071-0155-23",
        brand_name="Lipitor",
        generic_name="Atorvastatin Calcium",
        rxnorm_cui="310798",
        category="Statin (Lipid Lowering)",
        dosage_form="Tablet",
        strength="20mg",
        unit_cost=0.30,
        unit_selling_price=2.00,
        dispensing_tax_percent=5.0
    ),
    "00078-0357-15": MedicationEntry(
        ndc="00078-0357-15",
        brand_name="Diovan",
        generic_name="Valsartan",
        rxnorm_cui="313596",
        category="Antihypertensive (ARB)",
        dosage_form="Tablet",
        strength="80mg",
        unit_cost=0.45,
        unit_selling_price=2.50,
        dispensing_tax_percent=5.0
    ),
    "00064-0021-30": MedicationEntry(
        ndc="00064-0021-30",
        brand_name="Cordarone",
        generic_name="Amiodarone Hydrochloride",
        rxnorm_cui="308182",
        category="Antiarrhythmic",
        dosage_form="Ampoule (IV)",
        strength="150mg / 3mL",
        unit_cost=3.00,
        unit_selling_price=15.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),
    "00004-0058-01": MedicationEntry(
        ndc="00004-0058-01",
        brand_name="Levophed",
        generic_name="Norepinephrine Bitartrate",
        rxnorm_cui="312076",
        category="Vasopressor (ICU)",
        dosage_form="Ampoule (IV)",
        strength="4mg / 4mL",
        unit_cost=5.50,
        unit_selling_price=26.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),

    # --- Gastrointestinal & Endocrine ---
    "00008-0841-81": MedicationEntry(
        ndc="00008-0841-81",
        brand_name="Protonix",
        generic_name="Pantoprazole Sodium",
        rxnorm_cui="312292",
        category="Proton Pump Inhibitor (PPI)",
        dosage_form="Vial (IV)",
        strength="40mg",
        unit_cost=1.80,
        unit_selling_price=9.50,
        dispensing_tax_percent=5.0
    ),
    "00173-0442-02": MedicationEntry(
        ndc="00173-0442-02",
        brand_name="Zofran",
        generic_name="Ondansetron Hydrochloride",
        rxnorm_cui="312154",
        category="Antiemetic",
        dosage_form="Vial (IV)",
        strength="4mg / 2mL",
        unit_cost=0.90,
        unit_selling_price=6.50,
        dispensing_tax_percent=5.0
    ),
    "00002-7512-01": MedicationEntry(
        ndc="00002-7512-01",
        brand_name="Humalog",
        generic_name="Insulin Lispro",
        rxnorm_cui="311036",
        category="Insulin (Rapid Acting)",
        dosage_form="Vial (10mL)",
        strength="100 units/mL (1000u)",
        unit_cost=18.00,
        unit_selling_price=65.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True,
        requires_refrigeration=True
    ),
    "00024-5915-01": MedicationEntry(
        ndc="00024-5915-01",
        brand_name="Lantus",
        generic_name="Insulin Glargine",
        rxnorm_cui="311040",
        category="Insulin (Long Acting)",
        dosage_form="Solostar Pen (3mL)",
        strength="100 units/mL (300u)",
        unit_cost=22.00,
        unit_selling_price=78.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True,
        requires_refrigeration=True
    ),

    # --- IV Fluids & Electrolyte Infusions ---
    "00338-0017-04": MedicationEntry(
        ndc="00338-0017-04",
        brand_name="Normal Saline (0.9% NaCl)",
        generic_name="Sodium Chloride 0.9% IV Infusion",
        rxnorm_cui="313002",
        category="IV Fluid / Crystalloid",
        dosage_form="IV Bag",
        strength="1000mL",
        unit_cost=1.10,
        unit_selling_price=7.50,
        dispensing_tax_percent=5.0
    ),
    "00338-0117-04": MedicationEntry(
        ndc="00338-0117-04",
        brand_name="Ringer Lactate (Hartmann's)",
        generic_name="Lactated Ringer's Solution",
        rxnorm_cui="312891",
        category="IV Fluid / Crystalloid",
        dosage_form="IV Bag",
        strength="1000mL",
        unit_cost=1.25,
        unit_selling_price=8.00,
        dispensing_tax_percent=5.0
    ),
    "00338-0049-04": MedicationEntry(
        ndc="00338-0049-04",
        brand_name="Dextrose 5% in Water (D5W)",
        generic_name="5% Dextrose Injection",
        rxnorm_cui="310065",
        category="IV Fluid / Hydration",
        dosage_form="IV Bag",
        strength="1000mL",
        unit_cost=1.15,
        unit_selling_price=7.50,
        dispensing_tax_percent=5.0
    ),
    "00409-6651-06": MedicationEntry(
        ndc="00409-6651-06",
        brand_name="Potassium Chloride Concentrated",
        generic_name="Potassium Chloride Injection",
        rxnorm_cui="312528",
        category="Electrolyte Concentrate",
        dosage_form="Vial (IV Additive)",
        strength="20 mEq / 10mL",
        unit_cost=1.40,
        unit_selling_price=9.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),

    # --- Anesthetics, Sedatives & Emergency Code Blue ---
    "00074-4382-01": MedicationEntry(
        ndc="00074-4382-01",
        brand_name="Diprivan",
        generic_name="Propofol",
        rxnorm_cui="312615",
        category="General Anesthetic / Sedative",
        dosage_form="Vial (IV Emulsion)",
        strength="200mg / 20mL (1%)",
        unit_cost=4.20,
        unit_selling_price=22.00,
        dispensing_tax_percent=5.0,
        is_high_alert=True
    ),
    "00004-0015-01": MedicationEntry(
        ndc="00004-0015-01",
        brand_name="Versed",
        generic_name="Midazolam Hydrochloride",
        rxnorm_cui="311802",
        category="Sedative / Benzodiazepine",
        dosage_form="Vial (IV)",
        strength="5mg / 5mL",
        unit_cost=1.60,
        unit_selling_price=11.00,
        dispensing_tax_percent=0.0,
        is_controlled_substance=True,
        dea_schedule="Schedule IV"
    ),
    "00409-4911-34": MedicationEntry(
        ndc="00409-4911-34",
        brand_name="Adrenalin",
        generic_name="Epinephrine Auto-Injector / Ampoule",
        rxnorm_cui="310182",
        category="Emergency Resuscitation (Code Blue)",
        dosage_form="Ampoule (1:1000)",
        strength="1mg / 1mL",
        unit_cost=2.80,
        unit_selling_price=18.00,
        dispensing_tax_percent=0.0,
        is_high_alert=True
    ),
    "00409-1632-01": MedicationEntry(
        ndc="00409-1632-01",
        brand_name="Atropine Sulfate",
        generic_name="Atropine Injection",
        rxnorm_cui="308462",
        category="Anticholinergic / Bradycardia",
        dosage_form="Syringe (1:10000)",
        strength="1mg / 10mL",
        unit_cost=2.10,
        unit_selling_price=14.00,
        dispensing_tax_percent=0.0,
        is_high_alert=True
    )
}


def get_medication_entry(ndc: str) -> Optional[MedicationEntry]:
    """Retrieve medication details by NDC."""
    return PHARMACY_NDC_CATALOG.get(ndc)


def search_medications(query: str, limit: int = 15) -> List[MedicationEntry]:
    """Search pharmacy medication catalog by name, brand, generic, or category."""
    q = query.lower()
    matches = [
        med for med in PHARMACY_NDC_CATALOG.values()
        if q in med.brand_name.lower() or q in med.generic_name.lower() or q in med.category.lower() or q in med.ndc
    ]
    return matches[:limit]

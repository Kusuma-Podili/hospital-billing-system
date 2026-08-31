"""
MedBill Enterprise Catalogs - CPT & HCPCS Master Procedural Coding Catalog
Defines standardized American Medical Association CPT-4 and CMS HCPCS procedure codes,
relative value units (RVU Work, Practice Expense, Malpractice), baseline charges, and categories.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class CPTCodeEntry:
    code: str
    description: str
    category: str
    sub_category: str
    work_rvu: float
    pe_rvu: float  # Practice Expense RVU
    mp_rvu: float  # Malpractice RVU
    total_rvu: float
    standard_fee: float
    is_surgical: bool = False
    global_period_days: int = 0  # 0, 10, 90 days


# Standard conversion factor for baseline calculations
MEDICARE_CONVERSION_FACTOR_2026 = 33.2875

# Exhaustive CPT-4 & HCPCS Catalog
CPT_CATALOG: Dict[str, CPTCodeEntry] = {
    # --- Evaluation & Management (E&M) Outpatient Services ---
    "99202": CPTCodeEntry("99202", "Office/outpatient visit new patient, straightforward MDM 15-29 min", "E&M", "Outpatient New", 0.93, 1.10, 0.09, 2.12, 110.00),
    "99203": CPTCodeEntry("99203", "Office/outpatient visit new patient, low MDM 30-44 min", "E&M", "Outpatient New", 1.60, 1.48, 0.15, 3.23, 165.00),
    "99204": CPTCodeEntry("99204", "Office/outpatient visit new patient, moderate MDM 45-59 min", "E&M", "Outpatient New", 2.60, 2.22, 0.24, 5.06, 260.00),
    "99205": CPTCodeEntry("99205", "Office/outpatient visit new patient, high MDM 60-74 min", "E&M", "Outpatient New", 3.50, 2.85, 0.32, 6.67, 345.00),
    "99211": CPTCodeEntry("99211", "Office/outpatient visit established patient, minimal nurse visit", "E&M", "Outpatient Est", 0.18, 0.52, 0.02, 0.72, 45.00),
    "99212": CPTCodeEntry("99212", "Office/outpatient visit established patient, straightforward MDM 10-19 min", "E&M", "Outpatient Est", 0.70, 0.88, 0.07, 1.65, 85.00),
    "99213": CPTCodeEntry("99213", "Office/outpatient visit established patient, low MDM 20-29 min", "E&M", "Outpatient Est", 1.30, 1.18, 0.11, 2.59, 130.00),
    "99214": CPTCodeEntry("99214", "Office/outpatient visit established patient, moderate MDM 30-39 min", "E&M", "Outpatient Est", 1.92, 1.62, 0.16, 3.70, 190.00),
    "99215": CPTCodeEntry("99215", "Office/outpatient visit established patient, high MDM 40-54 min", "E&M", "Outpatient Est", 2.80, 2.14, 0.23, 5.17, 275.00),

    # --- Hospital Inpatient & Observation Care E&M ---
    "99221": CPTCodeEntry("99221", "Initial hospital inpatient/observation care, straightforward/low MDM 40 min", "E&M", "Inpatient Initial", 1.92, 1.25, 0.18, 3.35, 210.00),
    "99222": CPTCodeEntry("99222", "Initial hospital inpatient/observation care, moderate MDM 55 min", "E&M", "Inpatient Initial", 2.61, 1.68, 0.24, 4.53, 290.00),
    "99223": CPTCodeEntry("99223", "Initial hospital inpatient/observation care, high MDM 75 min", "E&M", "Inpatient Initial", 3.86, 2.30, 0.35, 6.51, 410.00),
    "99231": CPTCodeEntry("99231", "Subsequent hospital inpatient/observation care, straightforward/low MDM 25 min", "E&M", "Inpatient Subsequent", 1.00, 0.65, 0.09, 1.74, 115.00),
    "99232": CPTCodeEntry("99232", "Subsequent hospital inpatient/observation care, moderate MDM 35 min", "E&M", "Inpatient Subsequent", 1.59, 0.98, 0.14, 2.71, 175.00),
    "99233": CPTCodeEntry("99233", "Subsequent hospital inpatient/observation care, high MDM 50 min", "E&M", "Inpatient Subsequent", 2.40, 1.42, 0.21, 4.03, 260.00),
    "99238": CPTCodeEntry("99238", "Hospital discharge day management, 30 minutes or less", "E&M", "Inpatient Discharge", 1.50, 0.90, 0.13, 2.53, 160.00),
    "99239": CPTCodeEntry("99239", "Hospital discharge day management, more than 30 minutes", "E&M", "Inpatient Discharge", 2.20, 1.28, 0.19, 3.67, 240.00),

    # --- Emergency Department E&M ---
    "99281": CPTCodeEntry("99281", "Emergency department visit, straightforward triage", "E&M", "Emergency Dept", 0.45, 0.35, 0.04, 0.84, 95.00),
    "99282": CPTCodeEntry("99282", "Emergency department visit, low MDM", "E&M", "Emergency Dept", 0.93, 0.58, 0.08, 1.59, 150.00),
    "99283": CPTCodeEntry("99283", "Emergency department visit, moderate MDM", "E&M", "Emergency Dept", 1.60, 0.95, 0.14, 2.69, 240.00),
    "99284": CPTCodeEntry("99284", "Emergency department visit, high MDM with urgent threat", "E&M", "Emergency Dept", 2.74, 1.52, 0.23, 4.49, 395.00),
    "99285": CPTCodeEntry("99285", "Emergency department visit, high MDM with immediate life threat", "E&M", "Emergency Dept", 4.00, 2.10, 0.34, 6.44, 580.00),

    # --- Critical Care Services ---
    "99291": CPTCodeEntry("99291", "Critical care, evaluation and management of critically ill patient; first 30-74 min", "E&M", "Critical Care", 4.50, 2.20, 0.38, 7.08, 650.00),
    "99292": CPTCodeEntry("99292", "Critical care, each additional 30 minutes", "E&M", "Critical Care", 2.25, 1.10, 0.19, 3.54, 325.00),

    # --- Surgical Procedures ---
    "10060": CPTCodeEntry("10060", "Incision and drainage of abscess; simple or single", "Surgery", "Integumentary", 1.25, 2.45, 0.15, 3.85, 220.00, True, 10),
    "12001": CPTCodeEntry("12001", "Simple repair of superficial wounds of scalp, neck, axillae, trunk 2.5 cm or less", "Surgery", "Integumentary", 0.88, 1.95, 0.10, 2.93, 175.00, True, 0),
    "27447": CPTCodeEntry("27447", "Arthroplasty, knee, condyle and plateau; medial and lateral compartments (Total Knee)", "Surgery", "Orthopedic", 20.72, 14.50, 3.42, 38.64, 4200.00, True, 90),
    "27130": CPTCodeEntry("27130", "Arthroplasty, acetabular and proximal femoral prosthetic replacement (Total Hip)", "Surgery", "Orthopedic", 21.15, 15.20, 3.65, 40.00, 4450.00, True, 90),
    "33533": CPTCodeEntry("33533", "Coronary artery bypass, using arterial graft(s); single arterial graft (CABG)", "Surgery", "Cardiovascular", 32.50, 22.80, 5.80, 61.10, 7800.00, True, 90),
    "33534": CPTCodeEntry("33534", "Coronary artery bypass, using arterial graft(s); 2 coronary arterial grafts", "Surgery", "Cardiovascular", 37.80, 26.40, 6.70, 70.90, 8900.00, True, 90),
    "43239": CPTCodeEntry("43239", "Esophagogastroduodenoscopy (EGD), flexible, transoral; with biopsy", "Surgery", "Digestive", 2.19, 5.25, 0.35, 7.79, 780.00, True, 0),
    "44970": CPTCodeEntry("44970", "Laparoscopy, surgical, appendectomy", "Surgery", "Digestive", 8.95, 6.20, 1.45, 16.60, 2100.00, True, 90),
    "47562": CPTCodeEntry("47562", "Laparoscopic cholecystectomy", "Surgery", "Digestive", 10.50, 7.80, 1.70, 20.00, 2650.00, True, 90),
    "49505": CPTCodeEntry("49505", "Repair initial inguinal hernia, age 5 years or older; reducible", "Surgery", "Digestive", 6.85, 4.90, 1.10, 12.85, 1550.00, True, 90),
    "61154": CPTCodeEntry("61154", "Burr hole(s) with evacuation and/or drainage of hematoma, extradural or subdural", "Surgery", "Neurosurgery", 18.50, 12.60, 3.10, 34.20, 4800.00, True, 90),
    "66984": CPTCodeEntry("66984", "Extracapsular cataract removal with insertion of intraocular lens prosthesis", "Surgery", "Ophthalmology", 7.80, 8.40, 0.95, 17.15, 1850.00, True, 90),

    # --- Anesthesia Codes ---
    "00100": CPTCodeEntry("00100", "Anesthesia for procedures on salivary glands, including biopsy", "Anesthesia", "Head", 5.00, 0.00, 0.00, 5.00, 450.00),
    "00790": CPTCodeEntry("00790", "Anesthesia for intraperitoneal procedures in upper abdomen; laparoscopic", "Anesthesia", "Abdomen", 7.00, 0.00, 0.00, 7.00, 680.00),
    "00810": CPTCodeEntry("00810", "Anesthesia for lower intestinal endoscopic procedures", "Anesthesia", "Endoscopy", 5.00, 0.00, 0.00, 5.00, 480.00),
    "01400": CPTCodeEntry("01400", "Anesthesia for open or surgical arthroscopic procedures on knee joint", "Anesthesia", "Orthopedic", 4.00, 0.00, 0.00, 4.00, 550.00),
    "01967": CPTCodeEntry("01967", "Neuraxial labor analgesia/anesthesia for planned vaginal delivery", "Anesthesia", "Obstetric", 5.00, 0.00, 0.00, 5.00, 750.00),

    # --- Radiology & Diagnostic Imaging ---
    "71045": CPTCodeEntry("71045", "Radiologic examination, chest; single view", "Radiology", "X-Ray", 0.22, 0.48, 0.02, 0.72, 75.00),
    "71046": CPTCodeEntry("71046", "Radiologic examination, chest; 2 views", "Radiology", "X-Ray", 0.28, 0.65, 0.03, 0.96, 110.00),
    "70450": CPTCodeEntry("70450", "Computed tomography, head or brain; without contrast material", "Radiology", "CT Scan", 0.85, 3.45, 0.12, 4.42, 450.00),
    "70460": CPTCodeEntry("70460", "Computed tomography, head or brain; with contrast material", "Radiology", "CT Scan", 1.15, 4.80, 0.16, 6.11, 590.00),
    "71250": CPTCodeEntry("71250", "Computed tomography, thorax; without contrast material", "Radiology", "CT Scan", 1.16, 4.20, 0.15, 5.51, 520.00),
    "74177": CPTCodeEntry("74177", "Computed tomography, abdomen and pelvis; with contrast material(s)", "Radiology", "CT Scan", 1.82, 6.90, 0.25, 8.97, 850.00),
    "70551": CPTCodeEntry("70551", "Magnetic resonance (eg, proton) imaging, brain; without contrast", "Radiology", "MRI", 1.48, 6.80, 0.22, 8.50, 890.00),
    "70553": CPTCodeEntry("70553", "Magnetic resonance (eg, proton) imaging, brain; without and with contrast", "Radiology", "MRI", 2.25, 9.40, 0.32, 11.97, 1250.00),
    "76700": CPTCodeEntry("76700", "Ultrasound, abdominal, real time with image documentation; complete", "Radiology", "Ultrasound", 0.81, 2.65, 0.09, 3.55, 320.00),
    "93306": CPTCodeEntry("93306", "Echocardiography, transthoracic, real-time with image documentation, Doppler complete", "Radiology", "Cardiology", 1.30, 4.90, 0.18, 6.38, 620.00),

    # --- Pathology & Laboratory ---
    "80053": CPTCodeEntry("80053", "Comprehensive metabolic panel (CMP)", "Pathology", "Panels", 0.00, 0.00, 0.00, 0.00, 65.00),
    "85025": CPTCodeEntry("85025", "Blood count; complete (CBC) with automated differential", "Pathology", "Hematology", 0.00, 0.00, 0.00, 0.00, 45.00),
    "80061": CPTCodeEntry("80061", "Lipid panel (Total cholesterol, HDL, Triglycerides)", "Pathology", "Panels", 0.00, 0.00, 0.00, 0.00, 55.00),
    "84443": CPTCodeEntry("84443", "Thyroid stimulating hormone (TSH)", "Pathology", "Chemistry", 0.00, 0.00, 0.00, 0.00, 50.00),
    "82550": CPTCodeEntry("82550", "Creatine kinase (CK), (CPK); total", "Pathology", "Chemistry", 0.00, 0.00, 0.00, 0.00, 40.00),
    "84484": CPTCodeEntry("84484", "Troponin, quantitative", "Pathology", "Cardiac Markers", 0.00, 0.00, 0.00, 0.00, 75.00),
    "87635": CPTCodeEntry("87635", "Infectious agent detection by nucleic acid (DNA or RNA); SARS-CoV-2 (COVID-19)", "Pathology", "Microbiology", 0.00, 0.00, 0.00, 0.00, 110.00),
    "88305": CPTCodeEntry("88305", "Level IV - Surgical pathology, gross and microscopic examination", "Pathology", "Surgical Pathology", 0.75, 1.45, 0.08, 2.28, 195.00)
}


def get_cpt_entry(code: str) -> Optional[CPTCodeEntry]:
    """Retrieve CPT entry by code."""
    return CPT_CATALOG.get(code)


def search_cpt(query: str, limit: int = 15) -> List[CPTCodeEntry]:
    """Search CPT catalog by code, description, or category."""
    q = query.lower()
    matches = [
        entry for entry in CPT_CATALOG.values()
        if q in entry.code.lower() or q in entry.description.lower() or q in entry.category.lower() or q in entry.sub_category.lower()
    ]
    return matches[:limit]

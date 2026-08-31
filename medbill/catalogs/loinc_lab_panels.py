"""
MedBill Enterprise Catalogs - LOINC Laboratory Panels & Diagnostic Imaging Catalog
Defines comprehensive laboratory blood tests, pathology panels, imaging modalities (X-Ray, CT, MRI, Ultrasound),
STAT urgent turnaround multipliers, specimen handling, and pathologist interpretation fees.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class LabPanelEntry:
    loinc_code: str
    cpt_equivalent: str
    panel_name: str
    department: str  # Hematology, Biochemistry, Microbiology, Pathology, Radiology, Cardiology
    specimen_type: str  # Whole Blood, Serum, Plasma, Urine, Biopsy Tissue, CSF
    standard_price: float
    urgent_stat_multiplier: float  # typically 1.50 (+50% for 1-hour STAT turnaround)
    specimen_collection_fee: float  # Phlebotomy / sample handling
    professional_review_fee: float  # Pathologist / Radiologist reading
    turnaround_time_hours: int
    is_fasting_required: bool = False
    included_subtests: List[str] = field(default_factory=list)


# Exhaustive LOINC Laboratory & Diagnostic Catalog
LOINC_LAB_CATALOG: Dict[str, LabPanelEntry] = {
    # --- Hematology & Coagulation ---
    "58410-2": LabPanelEntry(
        loinc_code="58410-2",
        cpt_equivalent="85025",
        panel_name="Complete Blood Count (CBC) with 5-Part Differential",
        department="Hematology",
        specimen_type="Whole Blood (EDTA)",
        standard_price=45.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=15.00,
        turnaround_time_hours=2,
        included_subtests=["Hemoglobin", "Hematocrit", "RBC Count", "WBC Count", "Platelet Count", "MCV", "MCH", "MCHC", "Neutrophils", "Lymphocytes", "Monocytes", "Eosinophils", "Basophils"]
    ),
    "5902-2": LabPanelEntry(
        loinc_code="5902-2",
        cpt_equivalent="85610",
        panel_name="Prothrombin Time (PT) with INR",
        department="Hematology",
        specimen_type="Citrated Plasma",
        standard_price=35.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=10.00,
        turnaround_time_hours=2,
        included_subtests=["PT Seconds", "INR Ratio", "Control PT"]
    ),
    "3173-2": LabPanelEntry(
        loinc_code="3173-2",
        cpt_equivalent="85730",
        panel_name="Activated Partial Thromboplastin Time (aPTT)",
        department="Hematology",
        specimen_type="Citrated Plasma",
        standard_price=38.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=10.00,
        turnaround_time_hours=2,
        included_subtests=["aPTT Seconds", "Patient vs Control Ratio"]
    ),

    # --- Biochemistry, Renal & Liver Panels ---
    "24323-8": LabPanelEntry(
        loinc_code="24323-8",
        cpt_equivalent="80053",
        panel_name="Comprehensive Metabolic Panel (CMP 14-Parameters)",
        department="Biochemistry",
        specimen_type="Serum (Gel Separator)",
        standard_price=65.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=18.00,
        turnaround_time_hours=3,
        is_fasting_required=True,
        included_subtests=["Glucose", "BUN (Blood Urea Nitrogen)", "Creatinine", "eGFR", "Sodium", "Potassium", "Chloride", "Carbon Dioxide", "Calcium", "Total Protein", "Albumin", "Bilirubin Total", "Alkaline Phosphatase (ALP)", "AST (SGOT)", "ALT (SGPT)"]
    ),
    "24325-3": LabPanelEntry(
        loinc_code="24325-3",
        cpt_equivalent="80076",
        panel_name="Hepatic Function Liver Panel (LFT)",
        department="Biochemistry",
        specimen_type="Serum",
        standard_price=55.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=15.00,
        turnaround_time_hours=3,
        included_subtests=["Total Protein", "Albumin", "Globulin", "A/G Ratio", "Total Bilirubin", "Direct Bilirubin", "Indirect Bilirubin", "SGOT (AST)", "SGPT (ALT)", "Alkaline Phosphatase", "GGT"]
    ),
    "24362-6": LabPanelEntry(
        loinc_code="24362-6",
        cpt_equivalent="80069",
        panel_name="Renal Function Kidney Panel (KFT / RFT)",
        department="Biochemistry",
        specimen_type="Serum",
        standard_price=50.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=12.00,
        professional_review_fee=15.00,
        turnaround_time_hours=3,
        included_subtests=["Serum Creatinine", "Blood Urea", "BUN", "Uric Acid", "Sodium", "Potassium", "Chloride", "eGFR"]
    ),
    "24331-1": LabPanelEntry(
        loinc_code="24331-1",
        cpt_equivalent="80061",
        panel_name="Lipid Profile with Atherogenic Index",
        department="Biochemistry",
        specimen_type="Serum",
        standard_price=55.00,
        urgent_stat_multiplier=1.20,
        specimen_collection_fee=12.00,
        professional_review_fee=12.00,
        turnaround_time_hours=4,
        is_fasting_required=True,
        included_subtests=["Total Cholesterol", "HDL Cholesterol", "LDL Cholesterol", "VLDL Cholesterol", "Triglycerides", "Total Cholesterol / HDL Ratio", "Non-HDL Cholesterol"]
    ),
    "4548-4": LabPanelEntry(
        loinc_code="4548-4",
        cpt_equivalent="83036",
        panel_name="Glycated Hemoglobin (HbA1c)",
        department="Biochemistry",
        specimen_type="Whole Blood (EDTA)",
        standard_price=45.00,
        urgent_stat_multiplier=1.20,
        specimen_collection_fee=12.00,
        professional_review_fee=10.00,
        turnaround_time_hours=3,
        included_subtests=["HbA1c Percentage", "Estimated Average Glucose (eAG)"]
    ),

    # --- Cardiac Markers & Critical Care Emergency ---
    "6598-7": LabPanelEntry(
        loinc_code="6598-7",
        cpt_equivalent="84484",
        panel_name="High-Sensitivity Cardiac Troponin-I (hs-cTnI) Quantitative",
        department="Cardiology",
        specimen_type="Plasma / Serum",
        standard_price=85.00,
        urgent_stat_multiplier=1.60,
        specimen_collection_fee=15.00,
        professional_review_fee=25.00,
        turnaround_time_hours=1,
        included_subtests=["Troponin-I pg/mL", "99th Percentile Reference Limit Check"]
    ),
    "48425-3": LabPanelEntry(
        loinc_code="48425-3",
        cpt_equivalent="85379",
        panel_name="D-Dimer Quantitative (Fibrin Degradation)",
        department="Cardiology",
        specimen_type="Citrated Plasma",
        standard_price=75.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=15.00,
        professional_review_fee=20.00,
        turnaround_time_hours=1,
        included_subtests=["D-Dimer FEU ug/mL"]
    ),
    "33762-6": LabPanelEntry(
        loinc_code="33762-6",
        cpt_equivalent="83880",
        panel_name="NT-proBNP (N-Terminal Pro-B-Type Natriuretic Peptide)",
        department="Cardiology",
        specimen_type="Serum",
        standard_price=110.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=15.00,
        professional_review_fee=25.00,
        turnaround_time_hours=2,
        included_subtests=["NT-proBNP pg/mL"]
    ),
    "24338-6": LabPanelEntry(
        loinc_code="24338-6",
        cpt_equivalent="82803",
        panel_name="Arterial Blood Gas (ABG) with Lactate & Co-oximetry",
        department="Biochemistry",
        specimen_type="Heparinized Arterial Blood",
        standard_price=90.00,
        urgent_stat_multiplier=1.75,
        specimen_collection_fee=20.00,
        professional_review_fee=30.00,
        turnaround_time_hours=1,
        included_subtests=["pH", "pCO2", "pO2", "HCO3-", "Base Excess", "SaO2", "Lactate", "Electrolytes", "Methemoglobin", "Carboxyhemoglobin"]
    ),

    # --- Microbiology & Infectious Serology ---
    "94500-6": LabPanelEntry(
        loinc_code="94500-6",
        cpt_equivalent="87635",
        panel_name="SARS-CoV-2 (COVID-19) RT-PCR Multiplex Detection",
        department="Microbiology",
        specimen_type="Nasopharyngeal Swab",
        standard_price=95.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=15.00,
        professional_review_fee=20.00,
        turnaround_time_hours=6,
        included_subtests=["SARS-CoV-2 N Gene", "ORF1ab Gene", "Internal Control"]
    ),
    "600-7": LabPanelEntry(
        loinc_code="600-7",
        cpt_equivalent="87040",
        panel_name="Automated Blood Culture with Antibiotic Susceptibility (MIC)",
        department="Microbiology",
        specimen_type="Blood Culture Bottles (Aerobic & Anaerobic)",
        standard_price=80.00,
        urgent_stat_multiplier=1.20,
        specimen_collection_fee=18.00,
        professional_review_fee=25.00,
        turnaround_time_hours=48,
        included_subtests=["Organism Identification", "Minimum Inhibitory Concentration (MIC) Antibiogram"]
    ),

    # --- Radiology & Imaging Modalities ---
    "36554-4": LabPanelEntry(
        loinc_code="36554-4",
        cpt_equivalent="71046",
        panel_name="Digital Chest X-Ray (PA and Lateral Views)",
        department="Radiology",
        specimen_type="Radiographic Exposure",
        standard_price=85.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=0.00,
        professional_review_fee=40.00,
        turnaround_time_hours=2,
        included_subtests=["PA View Radiograph", "Lateral View Radiograph", "Radiologist Diagnostic Report"]
    ),
    "24627-2": LabPanelEntry(
        loinc_code="24627-2",
        cpt_equivalent="70450",
        panel_name="CT Head / Brain Non-Contrast Multi-Slice",
        department="Radiology",
        specimen_type="Helical Computed Tomography",
        standard_price=420.00,
        urgent_stat_multiplier=1.60,
        specimen_collection_fee=0.00,
        professional_review_fee=95.00,
        turnaround_time_hours=2,
        included_subtests=["Axial Reconstruction", "Sagittal MPR", "Coronal MPR", "Radiologist Report"]
    ),
    "24725-4": LabPanelEntry(
        loinc_code="24725-4",
        cpt_equivalent="74177",
        panel_name="CT Abdomen & Pelvis with Tri-Phasic IV Contrast",
        department="Radiology",
        specimen_type="Helical CT with Non-Ionic IV Contrast",
        standard_price=780.00,
        urgent_stat_multiplier=1.50,
        specimen_collection_fee=25.00,  # IV cannula placement
        professional_review_fee=150.00,
        turnaround_time_hours=4,
        is_fasting_required=True,
        included_subtests=["Arterial Phase", "Venous Phase", "Delayed Phase", "3D Vascular MIP", "Radiologist Report"]
    ),
    "24590-2": LabPanelEntry(
        loinc_code="24590-2",
        cpt_equivalent="70553",
        panel_name="High-Field 3T MRI Brain with Gadolinium Contrast",
        department="Radiology",
        specimen_type="Magnetic Resonance Imaging (3-Tesla)",
        standard_price=1150.00,
        urgent_stat_multiplier=1.40,
        specimen_collection_fee=25.00,
        professional_review_fee=220.00,
        turnaround_time_hours=6,
        included_subtests=["T1-Weighted", "T2-Weighted", "FLAIR", "DWI / ADC", "Post-Contrast T1 3D", "Radiologist Comprehensive Report"]
    ),
    "24606-6": LabPanelEntry(
        loinc_code="24606-6",
        cpt_equivalent="76700",
        panel_name="Complete Abdominal Ultrasound & Color Doppler",
        department="Radiology",
        specimen_type="Ultrasound Sonography",
        standard_price=280.00,
        urgent_stat_multiplier=1.40,
        specimen_collection_fee=0.00,
        professional_review_fee=75.00,
        turnaround_time_hours=2,
        is_fasting_required=True,
        included_subtests=["Liver Echo-texture", "Gallbladder", "Biliary Tree", "Pancreas", "Spleen", "Both Kidneys", "Urinary Bladder", "Color Flow Doppler"]
    )
}


def get_lab_panel(loinc_code: str) -> Optional[LabPanelEntry]:
    """Retrieve laboratory test panel by LOINC code."""
    return LOINC_LAB_CATALOG.get(loinc_code)


def search_lab_panels(query: str, limit: int = 15) -> List[LabPanelEntry]:
    """Search diagnostic catalog by name, code, department, or included test."""
    q = query.lower()
    matches = [
        panel for panel in LOINC_LAB_CATALOG.values()
        if q in panel.panel_name.lower() or q in panel.loinc_code.lower() or q in panel.cpt_equivalent.lower() or q in panel.department.lower()
    ]
    return matches[:limit]

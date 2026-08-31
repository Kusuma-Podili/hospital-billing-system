"""
MedBill Enterprise Catalogs - ICD-10-CM Master Diagnostic Catalog
Contains comprehensive international clinical diagnostic codes, chapters, DRG weights, and severity tiers.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ICD10Entry:
    code: str
    description: str
    chapter: str
    category: str
    drg_weight: float
    is_cc_mcc: str  # Non-CC, CC (Complication/Comorbidity), MCC (Major CC)
    severity_level: int  # 1 to 5


# Exhaustive ICD-10-CM Master Dataset
ICD10_CATALOG: Dict[str, ICD10Entry] = {
    # Chapter 1: Certain infectious and parasitic diseases (A00-B99)
    "A00.0": ICD10Entry("A00.0", "Cholera due to Vibrio cholerae 01, biovar cholerae", "Infectious", "Intestinal", 1.15, "CC", 3),
    "A00.9": ICD10Entry("A00.9", "Cholera, unspecified", "Infectious", "Intestinal", 1.05, "Non-CC", 2),
    "A02.0": ICD10Entry("A02.0", "Salmonella enteritis", "Infectious", "Intestinal", 0.95, "Non-CC", 2),
    "A04.7": ICD10Entry("A04.7", "Enterocolitis due to Clostridium difficile", "Infectious", "Intestinal", 1.65, "MCC", 4),
    "A08.0": ICD10Entry("A08.0", "Rotaviral enteritis", "Infectious", "Viral", 0.85, "Non-CC", 2),
    "A15.0": ICD10Entry("A15.0", "Tuberculosis of lung", "Infectious", "Mycobacterial", 1.85, "MCC", 4),
    "A31.0": ICD10Entry("A31.0", "Pulmonary mycobacterial infection", "Infectious", "Mycobacterial", 1.75, "CC", 3),
    "A40.0": ICD10Entry("A40.0", "Sepsis due to streptococcus, group A", "Infectious", "Sepsis", 2.45, "MCC", 5),
    "A40.1": ICD10Entry("A40.1", "Sepsis due to streptococcus, group B", "Infectious", "Sepsis", 2.40, "MCC", 5),
    "A41.01": ICD10Entry("A41.01", "Sepsis due to Methicillin susceptible Staphylococcus aureus", "Infectious", "Sepsis", 2.65, "MCC", 5),
    "A41.02": ICD10Entry("A41.02", "Sepsis due to Methicillin resistant Staphylococcus aureus (MRSA)", "Infectious", "Sepsis", 3.10, "MCC", 5),
    "A41.51": ICD10Entry("A41.51", "Sepsis due to Escherichia coli [E. coli]", "Infectious", "Sepsis", 2.50, "MCC", 5),
    "A41.52": ICD10Entry("A41.52", "Sepsis due to Pseudomonas aeruginosa", "Infectious", "Sepsis", 2.80, "MCC", 5),
    "A41.9": ICD10Entry("A41.9", "Sepsis, unspecified organism", "Infectious", "Sepsis", 2.35, "MCC", 5),
    "A48.1": ICD10Entry("A48.1", "Legionnaires disease", "Infectious", "Bacterial", 1.95, "MCC", 4),
    "A49.02": ICD10Entry("A49.02", "Methicillin resistant Staphylococcus aureus infection, unspecified site", "Infectious", "Bacterial", 1.45, "CC", 3),
    "B00.1": ICD10Entry("B00.1", "Herpesviral vesicular dermatitis", "Infectious", "Viral", 0.70, "Non-CC", 1),
    "B02.9": ICD10Entry("B02.9", "Zoster without complications", "Infectious", "Viral", 0.75, "Non-CC", 1),
    "B18.2": ICD10Entry("B18.2", "Chronic viral hepatitis C", "Infectious", "Viral Hepatitis", 1.35, "CC", 3),
    "B20": ICD10Entry("B20", "Human immunodeficiency virus [HIV] disease", "Infectious", "Viral", 2.20, "MCC", 4),
    "B34.2": ICD10Entry("B34.2", "Coronavirus infection, unspecified", "Infectious", "Viral", 1.25, "CC", 2),
    "B37.0": ICD10Entry("B37.0", "Candidal stomatitis", "Infectious", "Fungal", 0.60, "Non-CC", 1),
    "B44.0": ICD10Entry("B44.0", "Invasive pulmonary aspergillosis", "Infectious", "Fungal", 2.95, "MCC", 5),
    "B96.20": ICD10Entry("B96.20", "Unspecified Escherichia coli as cause of diseases classified elsewhere", "Infectious", "Bacterial", 0.80, "Non-CC", 2),

    # Chapter 2: Neoplasms (C00-D49)
    "C15.9": ICD10Entry("C15.9", "Malignant neoplasm of esophagus, unspecified", "Neoplasms", "Digestive", 2.80, "MCC", 4),
    "C16.9": ICD10Entry("C16.9", "Malignant neoplasm of stomach, unspecified", "Neoplasms", "Digestive", 2.75, "MCC", 4),
    "C18.9": ICD10Entry("C18.9", "Malignant neoplasm of colon, unspecified", "Neoplasms", "Digestive", 2.65, "MCC", 4),
    "C20": ICD10Entry("C20", "Malignant neoplasm of rectum", "Neoplasms", "Digestive", 2.55, "MCC", 4),
    "C22.0": ICD10Entry("C22.0", "Liver cell carcinoma", "Neoplasms", "Hepatobiliary", 3.15, "MCC", 5),
    "C25.9": ICD10Entry("C25.9", "Malignant neoplasm of pancreas, unspecified", "Neoplasms", "Pancreatic", 3.40, "MCC", 5),
    "C34.10": ICD10Entry("C34.10", "Malignant neoplasm of upper lobe, unspecified bronchus or lung", "Neoplasms", "Respiratory", 2.90, "MCC", 5),
    "C34.90": ICD10Entry("C34.90", "Malignant neoplasm of unsp part of unsp bronchus or lung", "Neoplasms", "Respiratory", 2.85, "MCC", 5),
    "C50.911": ICD10Entry("C50.911", "Malignant neoplasm of unsp site of right female breast", "Neoplasms", "Breast", 2.10, "CC", 3),
    "C50.912": ICD10Entry("C50.912", "Malignant neoplasm of unsp site of left female breast", "Neoplasms", "Breast", 2.10, "CC", 3),
    "C56.9": ICD10Entry("C56.9", "Malignant neoplasm of unspecified ovary", "Neoplasms", "Gynecologic", 2.60, "MCC", 4),
    "C61": ICD10Entry("C61", "Malignant neoplasm of prostate", "Neoplasms", "Genitourinary", 1.95, "CC", 3),
    "C64.9": ICD10Entry("C64.9", "Malignant neoplasm of unspecified kidney, except renal pelvis", "Neoplasms", "Genitourinary", 2.50, "MCC", 4),
    "C71.9": ICD10Entry("C71.9", "Malignant neoplasm of brain, unspecified", "Neoplasms", "Neurologic", 3.35, "MCC", 5),
    "C78.00": ICD10Entry("C78.00", "Secondary malignant neoplasm of unspecified lung", "Neoplasms", "Metastatic", 2.70, "MCC", 4),
    "C79.31": ICD10Entry("C79.31", "Secondary malignant neoplasm of brain", "Neoplasms", "Metastatic", 3.25, "MCC", 5),
    "C79.51": ICD10Entry("C79.51", "Secondary malignant neoplasm of bone", "Neoplasms", "Metastatic", 2.60, "MCC", 4),
    "C90.00": ICD10Entry("C90.00", "Multiple myeloma not having achieved remission", "Neoplasms", "Hematologic", 2.90, "MCC", 4),
    "C91.00": ICD10Entry("C91.00", "Acute lymphoblastic leukemia not having achieved remission", "Neoplasms", "Hematologic", 3.65, "MCC", 5),
    "C92.00": ICD10Entry("C92.00", "Acute myeloblastic leukemia not having achieved remission", "Neoplasms", "Hematologic", 3.80, "MCC", 5),
    "D50.9": ICD10Entry("D50.9", "Iron deficiency anemia, unspecified", "Hematologic", "Anemia", 0.75, "Non-CC", 1),
    "D64.9": ICD10Entry("D64.9", "Anemia, unspecified", "Hematologic", "Anemia", 0.80, "Non-CC", 1),
    "D69.6": ICD10Entry("D69.6", "Thrombocytopenia, unspecified", "Hematologic", "Coagulation", 1.25, "CC", 2),

    # Chapter 4: Endocrine, nutritional and metabolic diseases (E00-E89)
    "E03.9": ICD10Entry("E03.9", "Hypothyroidism, unspecified", "Endocrine", "Thyroid", 0.65, "Non-CC", 1),
    "E05.90": ICD10Entry("E05.90", "Thyrotoxicosis without thyrotoxic crisis or storm", "Endocrine", "Thyroid", 0.85, "Non-CC", 2),
    "E10.9": ICD10Entry("E10.9", "Type 1 diabetes mellitus without complications", "Endocrine", "Diabetes", 0.90, "Non-CC", 2),
    "E10.10": ICD10Entry("E10.10", "Type 1 diabetes mellitus with ketoacidosis without coma", "Endocrine", "Diabetes", 1.75, "MCC", 4),
    "E11.9": ICD10Entry("E11.9", "Type 2 diabetes mellitus without complications", "Endocrine", "Diabetes", 0.80, "Non-CC", 1),
    "E11.21": ICD10Entry("E11.21", "Type 2 diabetes mellitus with diabetic nephropathy", "Endocrine", "Diabetes", 1.35, "CC", 3),
    "E11.40": ICD10Entry("E11.40", "Type 2 diabetes mellitus with diabetic neuropathy, unspecified", "Endocrine", "Diabetes", 1.15, "CC", 2),
    "E11.65": ICD10Entry("E11.65", "Type 2 diabetes mellitus with hyperglycemia", "Endocrine", "Diabetes", 1.10, "Non-CC", 2),
    "E66.01": ICD10Entry("E66.01", "Morbid (severe) obesity due to excess calories", "Endocrine", "Metabolic", 1.10, "CC", 2),
    "E78.5": ICD10Entry("E78.5", "Hyperlipidemia, unspecified", "Endocrine", "Lipid", 0.55, "Non-CC", 1),
    "E86.0": ICD10Entry("E86.0", "Dehydration", "Endocrine", "Fluid/Electrolyte", 0.85, "Non-CC", 2),
    "E87.1": ICD10Entry("E87.1", "Hypo-osmolality and hyponatremia", "Endocrine", "Fluid/Electrolyte", 1.15, "CC", 3),
    "E87.2": ICD10Entry("E87.2", "Acidosis", "Endocrine", "Fluid/Electrolyte", 1.45, "CC", 3),
    "E87.5": ICD10Entry("E87.5", "Hyperkalemia", "Endocrine", "Fluid/Electrolyte", 1.30, "CC", 3),
    "E87.6": ICD10Entry("E87.6", "Hypokalemia", "Endocrine", "Fluid/Electrolyte", 1.05, "CC", 2),

    # Chapter 9: Diseases of the circulatory system (I00-I99)
    "I10": ICD10Entry("I10", "Essential (primary) hypertension", "Circulatory", "Hypertension", 0.65, "Non-CC", 1),
    "I11.0": ICD10Entry("I11.0", "Hypertensive heart disease with heart failure", "Circulatory", "Hypertension", 1.65, "MCC", 4),
    "I12.0": ICD10Entry("I12.0", "Hypertensive chronic kidney disease with stage 5 CKD or ESRD", "Circulatory", "Hypertension", 1.85, "MCC", 4),
    "I20.0": ICD10Entry("I20.0", "Unstable angina", "Circulatory", "Ischemic Heart", 1.40, "CC", 3),
    "I21.09": ICD10Entry("I21.09", "ST elevation (STEMI) myocardial infarction involving other coronary artery of anterior wall", "Circulatory", "Ischemic Heart", 2.95, "MCC", 5),
    "I21.19": ICD10Entry("I21.19", "ST elevation (STEMI) myocardial infarction involving other coronary artery of inferior wall", "Circulatory", "Ischemic Heart", 2.85, "MCC", 5),
    "I21.3": ICD10Entry("I21.3", "ST elevation (STEMI) myocardial infarction of unspecified site", "Circulatory", "Ischemic Heart", 2.90, "MCC", 5),
    "I21.4": ICD10Entry("I21.4", "Non-ST elevation (NSTEMI) myocardial infarction", "Circulatory", "Ischemic Heart", 2.45, "MCC", 5),
    "I25.10": ICD10Entry("I25.10", "Atherosclerotic heart disease of native coronary artery without angina pectoris", "Circulatory", "Ischemic Heart", 1.25, "Non-CC", 2),
    "I26.99": ICD10Entry("I26.99", "Other pulmonary embolism without acute cor pulmonale", "Circulatory", "Pulmonary Vascular", 2.25, "MCC", 4),
    "I48.0": ICD10Entry("I48.0", "Paroxysmal atrial fibrillation", "Circulatory", "Arrhythmia", 1.15, "Non-CC", 2),
    "I48.91": ICD10Entry("I48.91", "Unspecified atrial fibrillation", "Circulatory", "Arrhythmia", 1.10, "Non-CC", 2),
    "I49.01": ICD10Entry("I49.01", "Ventricular fibrillation", "Circulatory", "Arrhythmia", 3.20, "MCC", 5),
    "I50.22": ICD10Entry("I50.22", "Chronic systolic (congestive) heart failure", "Circulatory", "Heart Failure", 1.45, "CC", 3),
    "I50.23": ICD10Entry("I50.23", "Acute on chronic systolic (congestive) heart failure", "Circulatory", "Heart Failure", 2.15, "MCC", 4),
    "I50.9": ICD10Entry("I50.9", "Heart failure, unspecified", "Circulatory", "Heart Failure", 1.35, "CC", 3),
    "I63.9": ICD10Entry("I63.9", "Cerebral infarction, unspecified", "Circulatory", "Cerebrovascular", 2.35, "MCC", 4),
    "I61.9": ICD10Entry("I61.9", "Nontraumatic intracerebral hemorrhage, unspecified", "Circulatory", "Cerebrovascular", 3.40, "MCC", 5),
    "I70.209": ICD10Entry("I70.209", "Unspecified atherosclerosis of native arteries of extremities, unspecified extremity", "Circulatory", "Peripheral Vascular", 1.15, "Non-CC", 2),
    "I71.4": ICD10Entry("I71.4", "Abdominal aortic aneurysm, without rupture", "Circulatory", "Aneurysm", 2.10, "CC", 3),
    "I71.3": ICD10Entry("I71.3", "Abdominal aortic aneurysm, ruptured", "Circulatory", "Aneurysm", 4.50, "MCC", 5),

    # Chapter 10: Diseases of the respiratory system (J00-J99)
    "J01.90": ICD10Entry("J01.90", "Acute sinusitis, unspecified", "Respiratory", "Upper Respiratory", 0.50, "Non-CC", 1),
    "J06.9": ICD10Entry("J06.9", "Acute upper respiratory infection, unspecified", "Respiratory", "Upper Respiratory", 0.45, "Non-CC", 1),
    "J12.82": ICD10Entry("J12.82", "Pneumonia due to coronavirus disease 2019", "Respiratory", "Pneumonia", 2.15, "MCC", 4),
    "J15.9": ICD10Entry("J15.9", "Unspecified bacterial pneumonia", "Respiratory", "Pneumonia", 1.65, "CC", 3),
    "J18.9": ICD10Entry("J18.9", "Pneumonia, unspecified organism", "Respiratory", "Pneumonia", 1.55, "CC", 3),
    "J44.0": ICD10Entry("J44.0", "Chronic obstructive pulmonary disease with acute lower respiratory infection", "Respiratory", "COPD", 1.85, "MCC", 4),
    "J44.1": ICD10Entry("J44.1", "Chronic obstructive pulmonary disease with (acute) exacerbation", "Respiratory", "COPD", 1.60, "CC", 3),
    "J45.901": ICD10Entry("J45.901", "Unspecified asthma with (acute) exacerbation", "Respiratory", "Asthma", 1.25, "CC", 2),
    "J80": ICD10Entry("J80", "Acute respiratory distress syndrome (ARDS)", "Respiratory", "Critical Care", 3.85, "MCC", 5),
    "J96.00": ICD10Entry("J96.00", "Acute respiratory failure, unspecified with hypoxia or hypercapnia", "Respiratory", "Respiratory Failure", 2.65, "MCC", 5),
    "J96.01": ICD10Entry("J96.01", "Acute respiratory failure with hypoxia", "Respiratory", "Respiratory Failure", 2.75, "MCC", 5),

    # Chapter 11: Diseases of the digestive system (K00-K95)
    "K21.9": ICD10Entry("K21.9", "Gastro-esophageal reflux disease without esophagitis", "Digestive", "Esophageal", 0.55, "Non-CC", 1),
    "K25.0": ICD10Entry("K25.0", "Acute gastric ulcer with hemorrhage", "Digestive", "Gastric", 1.95, "MCC", 4),
    "K35.80": ICD10Entry("K35.80", "Unspecified acute appendicitis", "Digestive", "Appendix", 1.70, "CC", 3),
    "K35.2": ICD10Entry("K35.2", "Acute appendicitis with generalized peritonitis", "Digestive", "Appendix", 2.65, "MCC", 4),
    "K40.90": ICD10Entry("K40.90", "Unilateral inguinal hernia, without obstruction or gangrene, not specified as recurrent", "Digestive", "Hernia", 1.20, "Non-CC", 2),
    "K52.9": ICD10Entry("K52.9", "Noninfective gastroenteritis and colitis, unspecified", "Digestive", "Intestinal", 0.75, "Non-CC", 1),
    "K56.60": ICD10Entry("K56.60", "Unspecified intestinal obstruction", "Digestive", "Intestinal", 1.65, "CC", 3),
    "K70.30": ICD10Entry("K70.30", "Alcoholic cirrhosis of liver without ascites", "Digestive", "Hepatobiliary", 1.75, "CC", 3),
    "K70.31": ICD10Entry("K70.31", "Alcoholic cirrhosis of liver with ascites", "Digestive", "Hepatobiliary", 2.45, "MCC", 4),
    "K80.00": ICD10Entry("K80.00", "Calculus of gallbladder with acute cholecystitis without obstruction", "Digestive", "Gallbladder", 1.80, "CC", 3),
    "K85.90": ICD10Entry("K85.90", "Acute pancreatitis without necrosis or infection, unspecified", "Digestive", "Pancreas", 1.90, "CC", 4),
    "K92.2": ICD10Entry("K92.2", "Gastrointestinal hemorrhage, unspecified", "Digestive", "GI Bleed", 1.85, "MCC", 4),

    # Chapter 13: Diseases of the musculoskeletal system (M00-M99)
    "M16.11": ICD10Entry("M16.11", "Primary osteoarthritis, right hip", "Musculoskeletal", "Joint", 1.95, "Non-CC", 2),
    "M17.11": ICD10Entry("M17.11", "Primary osteoarthritis, right knee", "Musculoskeletal", "Joint", 1.90, "Non-CC", 2),
    "M17.12": ICD10Entry("M17.12", "Primary osteoarthritis, left knee", "Musculoskeletal", "Joint", 1.90, "Non-CC", 2),
    "M54.5": ICD10Entry("M54.5", "Low back pain", "Musculoskeletal", "Spine", 0.60, "Non-CC", 1),
    "M79.7": ICD10Entry("M79.7", "Fibromyalgia", "Musculoskeletal", "Soft Tissue", 0.70, "Non-CC", 1),
    "M80.08XA": ICD10Entry("M80.08XA", "Age-related osteoporosis with current pathological fracture, vertebra(e), init", "Musculoskeletal", "Bone", 1.85, "CC", 3),
    "M86.10": ICD10Entry("M86.10", "Other acute osteomyelitis, unspecified site", "Musculoskeletal", "Bone", 2.10, "MCC", 4),

    # Chapter 14: Diseases of the genitourinary system (N00-N99)
    "N17.9": ICD10Entry("N17.9", "Acute kidney failure, unspecified", "Genitourinary", "Renal", 1.95, "MCC", 4),
    "N18.3": ICD10Entry("N18.3", "Chronic kidney disease, stage 3 (moderate)", "Genitourinary", "Renal", 1.15, "Non-CC", 2),
    "N18.5": ICD10Entry("N18.5", "Chronic kidney disease, stage 5", "Genitourinary", "Renal", 1.80, "MCC", 4),
    "N18.6": ICD10Entry("N18.6", "End stage renal disease", "Genitourinary", "Renal", 2.05, "MCC", 4),
    "N20.1": ICD10Entry("N20.1", "Calculus of ureter", "Genitourinary", "Urinary Calculi", 1.10, "Non-CC", 2),
    "N39.0": ICD10Entry("N39.0", "Urinary tract infection, site not specified", "Genitourinary", "Infection", 0.90, "Non-CC", 2),
    "N40.1": ICD10Entry("N40.1", "Benign prostatic hyperplasia with lower urinary tract symptoms", "Genitourinary", "Prostate", 0.95, "Non-CC", 1),

    # Chapter 19: Injury, poisoning and certain other consequences of external causes (S00-T88)
    "S06.0X0A": ICD10Entry("S06.0X0A", "Concussion without loss of consciousness, initial encounter", "Injury", "Head Trauma", 1.10, "Non-CC", 2),
    "S06.5X9A": ICD10Entry("S06.5X9A", "Traumatic subdural hemorrhage with loss of consciousness, unspecified duration, init", "Injury", "Head Trauma", 3.45, "MCC", 5),
    "S72.001A": ICD10Entry("S72.001A", "Fracture of unspecified part of neck of right femur, init for clos fx", "Injury", "Fracture", 2.65, "CC", 3),
    "S72.002A": ICD10Entry("S72.002A", "Fracture of unspecified part of neck of left femur, init for clos fx", "Injury", "Fracture", 2.65, "CC", 3),
    "T81.4XXA": ICD10Entry("T81.4XXA", "Infection following a procedure, initial encounter", "Complications", "Surgical", 2.30, "MCC", 4),
    "T82.858A": ICD10Entry("T82.858A", "Thrombosis of other vascular prosthetic devices, implants and grafts, initial encounter", "Complications", "Vascular", 2.85, "MCC", 4),

    # Chapter 21: Factors influencing health status and contact with health services (Z00-Z99)
    "Z00.00": ICD10Entry("Z00.00", "Encounter for general adult medical examination without abnormal findings", "General Contact", "Exam", 0.40, "Non-CC", 1),
    "Z01.818": ICD10Entry("Z01.818", "Encounter for other preprocedural examination", "General Contact", "Pre-op", 0.50, "Non-CC", 1),
    "Z51.11": ICD10Entry("Z51.11", "Encounter for antineoplastic chemotherapy", "General Contact", "Oncology Therapy", 1.85, "Non-CC", 3),
    "Z99.11": ICD10Entry("Z99.11", "Dependence on respirator [ventilator] status", "General Contact", "Device Dependent", 2.95, "MCC", 5),
    "Z99.2": ICD10Entry("Z99.2", "Dependence on renal dialysis", "General Contact", "Device Dependent", 1.70, "CC", 3)
}


def get_icd10_entry(code: str) -> Optional[ICD10Entry]:
    """Retrieve an ICD-10 entry by exact code."""
    return ICD10_CATALOG.get(code)


def search_icd10(query: str, limit: int = 15) -> List[ICD10Entry]:
    """Search ICD-10 catalog by code or description."""
    q = query.lower()
    matches = [
        entry for entry in ICD10_CATALOG.values()
        if q in entry.code.lower() or q in entry.description.lower() or q in entry.category.lower()
    ]
    return matches[:limit]

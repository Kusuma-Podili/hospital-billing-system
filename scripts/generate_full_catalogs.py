"""
MedBill Enterprise - Full Scale Catalog & Dataset Synthesizer
Generates comprehensive clinical master catalogs and seed data for enterprise hospital billing scale.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOGS_DIR = os.path.join(PROJECT_ROOT, "medbill", "catalogs")
DB_DIR = os.path.join(PROJECT_ROOT, "medbill", "database")
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(CATALOGS_DIR, exist_ok=True)


def generate_icd10_full():
    filepath = os.path.join(CATALOGS_DIR, "icd10_cm_full.py")
    chapters = [
        ("Infectious", "A", "Infectious and Parasitic Diseases", 1.2, "CC", 3),
        ("Neoplasms", "C", "Malignant and Benign Neoplasms", 2.8, "MCC", 5),
        ("Hematology", "D", "Diseases of Blood and Blood-forming Organs", 1.1, "CC", 2),
        ("Endocrine", "E", "Endocrine, Nutritional and Metabolic Diseases", 0.9, "Non-CC", 2),
        ("MentalHealth", "F", "Mental and Behavioral Disorders", 1.0, "Non-CC", 2),
        ("NervousSystem", "G", "Diseases of the Nervous System", 2.2, "MCC", 4),
        ("Ophthalmology", "H", "Diseases of the Eye and Adnexa", 0.8, "Non-CC", 1),
        ("Cardiovascular", "I", "Diseases of the Circulatory System", 2.4, "MCC", 5),
        ("Respiratory", "J", "Diseases of the Respiratory System", 1.9, "MCC", 4),
        ("Gastrointestinal", "K", "Diseases of the Digestive System", 1.6, "CC", 3),
        ("Dermatology", "L", "Diseases of the Skin and Subcutaneous Tissue", 0.7, "Non-CC", 1),
        ("Orthopedic", "M", "Diseases of the Musculoskeletal System", 1.8, "CC", 3),
        ("Genitourinary", "N", "Diseases of the Genitourinary System", 1.5, "CC", 3),
        ("Obstetric", "O", "Pregnancy, Childbirth and the Puerperium", 1.4, "CC", 3),
        ("Perinatal", "P", "Conditions in the Perinatal Period", 2.5, "MCC", 4),
        ("Congenital", "Q", "Congenital Malformations and Anomalies", 2.1, "CC", 3),
        ("Trauma", "S", "Injury and External Causes", 2.0, "MCC", 4),
        ("HealthFactors", "Z", "Factors Influencing Health Status", 0.5, "Non-CC", 1),
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('"""\nMedBill Enterprise - Full ICD-10-CM Clinical Diagnostic Coding Catalog\n"""\n\n')
        f.write("from typing import Dict\nfrom medbill.catalogs.icd10_cm import ICD10Entry\n\n")
        f.write("ICD10_FULL_CATALOG: Dict[str, ICD10Entry] = {\n")
        
        count = 0
        for ch_name, prefix, desc_prefix, base_wt, cc_stat, base_sev in chapters:
            for cat in range(10, 99):
                for sub in range(0, 10):
                    code = f"{prefix}{cat}.{sub}"
                    desc = f"{desc_prefix} - Clinical Entity Category {cat} Subtype {sub}"
                    wt = round(base_wt + (cat % 5) * 0.15 + (sub * 0.05), 3)
                    sev = min(5, max(1, base_sev + (sub % 2)))
                    f.write(f'    "{code}": ICD10Entry("{code}", "{desc}", "{ch_name}", "Category_{prefix}{cat}", {wt}, "{cc_stat}", {sev}),\n')
                    count += 1
        f.write("}\n")
    print(f"Generated {count} ICD-10 entries in icd10_cm_full.py")


def generate_cpt_full():
    filepath = os.path.join(CATALOGS_DIR, "cpt_codes_full.py")
    categories = [
        ("E&M", "Evaluation and Management Services", 99000, 99999, 120.0, False, 0),
        ("Surgery_Integumentary", "Surgical Integumentary Procedures", 10000, 19999, 350.0, True, 10),
        ("Surgery_Musculoskeletal", "Surgical Musculoskeletal & Orthopedics", 20000, 29999, 2400.0, True, 90),
        ("Surgery_Respiratory", "Surgical Respiratory Procedures", 30000, 32999, 1800.0, True, 90),
        ("Surgery_Cardiovascular", "Surgical Cardiovascular & Vascular", 33000, 39999, 4500.0, True, 90),
        ("Surgery_Digestive", "Surgical Digestive Procedures", 40000, 49999, 1950.0, True, 90),
        ("Surgery_Genitourinary", "Surgical Genitourinary Procedures", 50000, 59999, 2100.0, True, 90),
        ("Surgery_Nervous", "Surgical Neurosurgery & Spine", 60000, 69999, 4800.0, True, 90),
        ("Radiology_Diagnostic", "Diagnostic Radiology & CT/MRI Imaging", 70000, 79999, 450.0, False, 0),
        ("Pathology_Lab", "Pathology and Laboratory Panels", 80000, 89999, 75.0, False, 0),
        ("Medicine_Clinical", "Clinical Medicine and Specialty Services", 90000, 98999, 180.0, False, 0),
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('"""\nMedBill Enterprise - Full CPT-4 & HCPCS Procedural Coding Catalog\n"""\n\n')
        f.write("from typing import Dict\nfrom medbill.catalogs.cpt_codes import CPTCodeEntry\n\n")
        f.write("CPT_FULL_CATALOG: Dict[str, CPTCodeEntry] = {\n")

        count = 0
        for cat_name, desc_prefix, start_code, end_code, base_fee, is_surg, global_days in categories:
            step = max(1, (end_code - start_code) // 1000)
            for code_num in range(start_code, end_code, step):
                code = str(code_num)
                desc = f"{desc_prefix} - Procedure Protocol Code #{code}"
                w_rvu = round(1.2 + (code_num % 100) * 0.1, 2)
                pe_rvu = round(0.8 + (code_num % 50) * 0.05, 2)
                mp_rvu = round(0.1 + (code_num % 20) * 0.01, 2)
                tot_rvu = round(w_rvu + pe_rvu + mp_rvu, 2)
                fee = round(base_fee + (code_num % 200) * 2.5, 2)
                f.write(f'    "{code}": CPTCodeEntry("{code}", "{desc}", "{cat_name}", "Subtype_{code_num % 10}", {w_rvu}, {pe_rvu}, {mp_rvu}, {tot_rvu}, {fee}, {is_surg}, {global_days}),\n')
                count += 1
        f.write("}\n")
    print(f"Generated {count} CPT entries in cpt_codes_full.py")


def generate_pharmacy_full():
    filepath = os.path.join(CATALOGS_DIR, "pharmacy_ndc_full.py")
    therapeutic_classes = [
        ("Antibacterial", "Capsule", "500mg", 0.8, 3.5, 5.0, False, None),
        ("Antiviral", "Tablet", "200mg", 1.5, 6.0, 5.0, False, None),
        ("Analgesic_Opioid", "Ampoule", "50mcg/mL", 2.0, 12.0, 0.0, True, "Schedule II"),
        ("Analgesic_NSAID", "Tablet", "400mg", 0.3, 1.8, 5.0, False, None),
        ("Antihypertensive", "Tablet", "10mg", 0.4, 2.2, 5.0, False, None),
        ("Antiarrhythmic", "Vial", "150mg/3mL", 3.2, 16.0, 5.0, False, None),
        ("Anticoagulant", "Syringe", "40mg/0.4mL", 5.5, 24.0, 5.0, False, None),
        ("Antidiabetic_Insulin", "Vial", "100u/mL", 15.0, 65.0, 5.0, False, None),
        ("Antineoplastic_Chemo", "Infusion", "100mg/50mL", 85.0, 320.0, 5.0, False, None),
        ("IV_Crystalloid", "IV Bag", "1000mL", 1.2, 8.0, 5.0, False, None),
        ("Anesthetic_General", "Vial", "200mg/20mL", 4.0, 20.0, 5.0, False, None),
        ("Sedative_Hypnotic", "Vial", "5mg/5mL", 1.8, 10.0, 0.0, True, "Schedule IV"),
    ]

    with open(filepath, "w", encoding="utf-8") as f:
        f.write('"""\nMedBill Enterprise - Full NDC & RxNorm Pharmaceutical Catalog\n"""\n\n')
        f.write("from typing import Dict\nfrom medbill.catalogs.pharmacy_ndc import MedicationEntry\n\n")
        f.write("PHARMACY_FULL_CATALOG: Dict[str, MedicationEntry] = {\n")

        count = 0
        for cat_name, dosage, strength, cost, price, tax, is_ctrl, sched in therapeutic_classes:
            for labeler in range(100, 999):
                ndc = f"00{labeler:03d}-{count % 9000 + 1000:04d}-01"
                brand = f"Med_{cat_name}_{labeler}"
                generic = f"Generic_{cat_name}_Formulation_{labeler}"
                rxcui = str(100000 + count)
                f.write(f'    "{ndc}": MedicationEntry("{ndc}", "{brand}", "{generic}", "{rxcui}", "{cat_name}", "{dosage}", "{strength}", {cost}, {price}, {tax}, {is_ctrl}, {repr(sched)}),\n')
                count += 1
        f.write("}\n")
    print(f"Generated {count} NDC medication entries in pharmacy_ndc_full.py")


def generate_database_seeds():
    filepath = os.path.join(DB_DIR, "seed_data.py")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write('"""\nMedBill Enterprise - Master Database Seeders\n"""\n\n')
        f.write("from typing import List, Dict, Any\n\n")
        f.write("SEED_PATIENTS: List[Dict[str, Any]] = [\n")
        for i in range(1, 3001):
            f.write(f'    {{"patient_id": "PAT_{i:06d}", "mrn": "MRN-{i:06d}", "first_name": "PatientFirstName_{i}", "last_name": "LastName_{i}", "dob": "19{70 + i % 30:02d}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}", "gender": "{"MALE" if i % 2 == 0 else "FEMALE"}", "phone": "555-{i:04d}", "blood_group": "{"O+" if i % 4 == 0 else ("A+" if i % 4 == 1 else "B+")}", "insurance_id": "POL_{i:04d}"}},\n')
        f.write("]\n\n")

        f.write("SEED_ENCOUNTERS: List[Dict[str, Any]] = [\n")
        for i in range(1, 5001):
            enc_type = "OUTPATIENT" if i % 3 == 0 else ("INPATIENT" if i % 3 == 1 else "EMERGENCY")
            f.write(f'    {{"encounter_id": "ENC_{i:06d}", "patient_id": "PAT_{i % 3000 + 1:06d}", "type": "{enc_type}", "admission_date": "2026-08-{(i % 30) + 1:02d}T09:00:00", "primary_icd10": "I10", "doctor_id": "DOC_{i % 50 + 1:03d}", "billed_amount": {150.0 + (i % 200) * 15.5:.2f}, "status": "CLOSED"}},\n')
        f.write("]\n\n")

        f.write("SEED_LEDGER_TRANSACTIONS: List[Dict[str, Any]] = [\n")
        for i in range(1, 5001):
            amt = round(250.0 + (i % 500) * 12.75, 2)
            f.write(f'    {{"txn_id": "TXN_{i:06d}", "invoice_id": "INV_{i:06d}", "entry_number": "JE-{i:06d}", "amount": {amt}, "debit_account": "1110", "credit_account": "4010", "status": "POSTED", "hash": "sha256_{i:08x}"}},\n')
        f.write("]\n")
    print(f"Generated comprehensive seed data in seed_data.py")


if __name__ == "__main__":
    generate_icd10_full()
    generate_cpt_full()
    generate_pharmacy_full()
    generate_database_seeds()

# 🏥 MedBill Enterprise - Hospital Billing & Revenue Cycle Management (RCM) System

An enterprise-grade healthcare financial and hospital billing platform designed to calculate consultation charges, pharmacy/medication dispensing, room/bed allocation tariffs, laboratory diagnostics, surgical procedure packages, insurance claims adjudication (CMS-1500 / UB-04 / HL7 FHIR R4), and split-payer invoicing with double-entry general ledger bookkeeping.

---

## 📋 Dependencies

The application relies on standard Python packages listed in `requirements.txt`:
- **Python**: `>= 3.10`
- **FastAPI**: `^0.110.0` (RESTful API framework)
- **Uvicorn**: `^0.28.0` (ASGI Web Server)
- **Pydantic**: `^2.6.0` (Data validation and models)
- **Jinja2**: `^3.1.3` (Template engine)
- **PyTest**: `^8.0.0` (Automated test suite)

Manifest files: `requirements.txt`, `pyproject.toml`, `package.json`  
Lockfiles: `requirements.lock`, `poetry.lock`, `package-lock.json`

---

## 🔧 Installation

To set up and install MedBill Enterprise locally:

### Option A: Using Python virtual environment (Recommended)
```bash
# 1. Clone the repository
git clone https://github.com/Kusuma-Podili/hospital-billing-system.git
cd hospital-billing-system

# 2. Create and activate virtual environment
python -m venv venv
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# 3. Install required dependencies
pip install -r requirements.txt
```

### Option B: Using Poetry
```bash
poetry install
```

### Option C: Using npm / Make
```bash
make install
```

---

## 🏗️ Build

To compile and verify the application build:

### Local Python Bytecode Compilation:
```bash
# Using Python
python -m compileall medbill

# Using Make
make build

# Using npm
npm run build
```

### Containerized Docker Build:
```bash
docker build -t medbill-enterprise:latest .
```

---

## 🚀 Run

### 1. Launch Web POS & RCM Dashboard Server
```bash
# Direct Python execution:
python main.py

# Or using Make:
make run

# Or using npm:
npm start

# Or using Docker:
docker run -p 8080:8080 medbill-enterprise:latest
```

The Web Dashboard will be available at **`http://localhost:8080`**.

### 2. Run Automated Verification Test Suites
```bash
# Execute master test runner:
python tests/runner.py

# Or using standard unittest:
python -m unittest discover -s tests -p "test_*.py"

# Or using pytest:
pytest tests/
```

---

## 💡 Usage & Features

### 1. 🩺 Clinical Consultation Billing Engine
- **Specialty Fee Schedules**: 20+ clinical specialties (Cardiology, Neurosurgery, Oncology, Orthopedics, Pediatrics, Nephrology, Internal Medicine).
- **Seniority Multipliers**: Junior Resident (0.7x), Attending Physician (1.0x), Senior Consultant (1.4x), Department Head (1.8x), Professor (2.2x).
- **Emergency Triage Escalations**: Level 1 Resuscitation (2.5x), Level 2 Emergent (2.0x), Level 3 Urgent (1.5x).
- **Out-of-Hours Surcharges**: Night on-call (+30%), Weekend (+20%).
- **Complimentary Follow-up Rules**: Automatically waives consultation fees within the 7-14 day window.

### 2. 🛏️ Hospital Bed & Room Tariff Engine
- **Ward & Suite Categories**: General Wards, Semi-Private, Single Deluxe, Super Deluxe, ICU, CCU, NICU, PICU, HDU, Isolation Wards, Daycare Beds.
- **Midnight Census Billing**: Daily census and partial hourly stay calculations.
- **Intensive Care Metered Tariffs**: Hourly metered medical oxygen ($25-$35/hr), mechanical ventilation ($125/hr), continuous telemetry monitoring ($35-$50/hr), and infusion syringe pumps.

### 3. 💊 Pharmacy Dispensing & Medication Tariffs
- **National Drug Code (NDC) & RxNorm Catalog**: Comprehensive medication catalog covering antibiotics, analgesics, cardiovascular, oncology infusions, controlled substances, and code blue emergency drugs.
- **Patient Safety Checks**: Automated rejection of expired drug lots and batch tracking.
- **Dispensing Taxes & Compounding**: Tiered VAT/GST calculations and cleanroom sterile IV compounding markups.

### 4. 🔬 Diagnostic Laboratory & Radiology Tariff Engine
- **LOINC Master Panels**: Complete Blood Count (CBC), Comprehensive Metabolic Panel (CMP), Cardiac Troponin-I, Arterial Blood Gas (ABG), 3T MRI, Multi-slice CT, and Ultrasound.
- **Urgent STAT Surcharges**: Automatic +50% multiplier for 1-hour STAT emergency processing.
- **Multi-Panel Bundles**: Automatic 10% bundle discounts for comprehensive health checkups.

### 5. 🔪 Surgical Operating Theater (OT) Costing
- **Multi-Tier Procedure Costing**: Laparoscopic Cholecystectomy, Appendectomy, Total Knee Replacement (TKR), Total Hip Replacement (THR), Coronary Artery Bypass (CABG), and Craniotomy.
- **Component Breakdown**: OT Table hourly rates, Chief Surgeon fees, Co-Surgeon/Assistant fees, Anesthesiologist fees, sterile consumable packs, titanium prosthetics implants, and Post-Anesthesia Care Unit (PACU) recovery room charges.

### 6. 🛡️ Health Insurance, TPA Adjudication & HL7 FHIR R4
- **Real-Time Adjudication**: Contractual PPO discounts, annual deductible accumulators, fixed co-pays, 80/20 co-insurance, and annual out-of-pocket maximum (OOPM) capping.
- **CMS-1500 & UB-04 Generation**: Structured JSON representations of HCFA-1500 and UB-04 claims.
- **HL7 FHIR Release 4 Integration**: Generates compliant `Account`, `Coverage`, `Claim`, `ClaimResponse`, and `ExplanationOfBenefit` (EOB) resources.

### 7. ⚖️ Double-Entry Financial Ledger & Split-Billing
- **Strict Mathematical Integrity**: Every generated invoice creates balanced debit and credit journal entries.
- **Dynamic Multi-Payer Split**: Divides invoices across Primary Insurance, Corporate Employer Sponsorship, Charity Hardship Waivers, and Patient Out-of-Pocket.
- **Immutable Audit Trail**: SHA-256 cryptographic hash chaining for every journal entry.

---

## 💻 CLI Commands

```bash
# Search clinical diagnosis codes
python medbill/cli.py search icd10 "sepsis"

# Search procedural and surgical codes
python medbill/cli.py search cpt "knee"

# Search medications in NDC catalog
python medbill/cli.py search pharmacy "augmentin"

# View real-time Double-Entry General Ledger Trial Balance
python medbill/cli.py ledger
```

---

## 🏛️ System Architecture

```
health/
├── main.py                    # Primary application entry point
├── app.py                     # Alternative runner entry point
├── Dockerfile                 # Containerized deployment manifest
├── Makefile                   # Build and test lifecycle targets
├── package.json               # Node/npm scripts & metadata
├── pyproject.toml             # Poetry build configuration
├── requirements.txt           # Python dependency manifest
├── requirements.lock          # Frozen lockfile
├── medbill/
│   ├── core/                  # Domain models, data structures, and exceptions
│   ├── pricing/               # 15 domain pricing & tariff engines
│   ├── clinical_rules/        # 10 clinical rules & medical necessity matrices
│   ├── insurance_tpa/         # 10 claims adjudication & EDI engines
│   ├── fhir/                  # 8 HL7 FHIR Release 4 financial services
│   ├── ledger/                # 8 double-entry general ledger & audit services
│   ├── billing_engine/        # Master invoice aggregator & split-billing services
│   ├── rcm_analytics/         # 7 accounts receivable & denial analytics services
│   ├── compliance/            # 5 HIPAA audit & price transparency guards
│   ├── catalogs/              # Standard medical coding & fee schedules
│   ├── web/                   # HTTP REST API server & web dashboard
│   └── cli.py                 # Command line interface tool
└── tests/                     # Automated unit & integration test suites
    ├── test_consultation_tariff.py
    ├── test_room_bed_tariff.py
    ├── test_pharmacy_billing.py
    ├── test_lab_diagnostics.py
    ├── test_surgical_costing.py
    ├── test_insurance_adjudication.py
    ├── test_fhir_financial.py
    ├── test_double_entry_ledger.py
    ├── test_split_billing.py
    └── runner.py              # Master test runner & metrics reporter
```

---

## 🔒 Proprietary Notice
Copyright (c) 2026 Kusuma Podili. All rights reserved. Proprietary and confidential.

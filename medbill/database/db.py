"""
MedBill Enterprise - SQLite Relational Database Engine
Provides ACID-compliant persistent database models, connection management,
schema migrations, and initial hospital seed data.
"""

import sqlite3
import os
import hashlib
import uuid
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "hospital_billing.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def hash_password(password: str) -> str:
    """Hashes a password with SHA-256 and a constant salt."""
    salt = "medbill_secure_hospital_salt_2026"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verifies a plain password against its SHA-256 hash."""
    return hash_password(password) == password_hash


def init_database():
    """Initializes all database tables, constraints, indexes, and seeds initial data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users / Admin Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL DEFAULT 'ADMIN',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 2. Settings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hospital_name TEXT NOT NULL DEFAULT 'Memorial Medical Hospital',
        hospital_address TEXT DEFAULT '124 Healthcare Avenue, Medical District',
        hospital_phone TEXT DEFAULT '+91 98765 43210',
        hospital_email TEXT DEFAULT 'billing@memorialhospital.in',
        tax_id TEXT DEFAULT 'GSTIN27AAACM1234F1Z5',
        currency_symbol TEXT DEFAULT '₹',
        default_tax_rate REAL DEFAULT 5.0,
        invoice_footer TEXT DEFAULT 'Thank you for choosing Memorial Medical Hospital. Wishing you good health!',
        updated_at TEXT NOT NULL
    )
    """)

    # 3. Cost Types Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cost_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 4. Services Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_code TEXT UNIQUE NOT NULL,
        service_name TEXT NOT NULL,
        cost_type_id INTEGER NOT NULL,
        description TEXT,
        price REAL NOT NULL CHECK(price >= 0),
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (cost_type_id) REFERENCES cost_types(id) ON DELETE RESTRICT
    )
    """)

    # 5. Patients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_number TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL CHECK(age >= 0),
        gender TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT,
        doctor TEXT,
        room_number TEXT,
        admission_date TEXT,
        discharge_date TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)

    # 6. Bills Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_number TEXT UNIQUE NOT NULL,
        patient_id INTEGER NOT NULL,
        bill_date TEXT NOT NULL,
        subtotal REAL NOT NULL DEFAULT 0.0,
        discount REAL NOT NULL DEFAULT 0.0,
        tax_percent REAL NOT NULL DEFAULT 0.0,
        tax_amount REAL NOT NULL DEFAULT 0.0,
        total_amount REAL NOT NULL DEFAULT 0.0,
        paid_amount REAL NOT NULL DEFAULT 0.0,
        balance_amount REAL NOT NULL DEFAULT 0.0,
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        bill_status TEXT NOT NULL DEFAULT 'Pending',
        notes TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE RESTRICT
    )
    """)

    # 7. Bill Items Table (with snapshot unit prices and cost type names)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bill_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER NOT NULL,
        service_id INTEGER,
        service_name TEXT NOT NULL,
        cost_type_name TEXT NOT NULL,
        unit_price REAL NOT NULL,
        quantity REAL NOT NULL CHECK(quantity > 0),
        amount REAL NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE,
        FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL
    )
    """)

    # 8. Payments Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        payment_number TEXT UNIQUE NOT NULL,
        bill_id INTEGER NOT NULL,
        amount REAL NOT NULL CHECK(amount > 0),
        payment_method TEXT NOT NULL,
        payment_date TEXT NOT NULL,
        reference_number TEXT,
        notes TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (bill_id) REFERENCES bills(id) ON DELETE CASCADE
    )
    """)

    # Create Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bills_patient ON bills(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(payment_status, bill_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bill_items_bill ON bill_items(bill_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_bill ON payments(bill_id)")

    conn.commit()

    # Seed Initial Data if tables are empty
    seed_initial_data(conn)
    conn.close()


def seed_initial_data(conn: sqlite3.Connection):
    """Seeds default admin, hospital settings, cost types, services, sample patients and sample bills."""
    cursor = conn.cursor()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    today = date.today().isoformat()

    # 1. Seed Admin User (default credentials: admin / admin)
    cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE username = 'admin'")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, role, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "admin",
            hash_password("admin"),
            "Hospital Administrator",
            "admin@memorialhospital.in",
            "ADMIN",
            now,
            now
        ))

    # 2. Seed Settings
    cursor.execute("SELECT COUNT(*) as cnt FROM settings")
    if cursor.fetchone()["cnt"] == 0:
        cursor.execute("""
        INSERT INTO settings (hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "Memorial Medical Hospital",
            "124 Healthcare Avenue, Medical District, Mumbai",
            "+91 98765 43210",
            "billing@memorialhospital.in",
            "GSTIN27AAACM1234F1Z5",
            "₹",
            5.0,
            "Thank you for choosing Memorial Medical Hospital. Wishing you a swift recovery!",
            now
        ))

    # 3. Seed Standard Cost Types
    cost_types_data = [
        ("Consultation", "Doctor OPD, specialist, and emergency consultation fees", 1),
        ("Room Charges", "Inpatient ward, private room, deluxe suite, and ICU bed stay charges", 1),
        ("Medicine", "Pharmaceutical drugs, antibiotics, injections, and IV fluids", 1),
        ("Laboratory Test", "Pathology, biochemistry, hematology, and microbiological tests", 1),
        ("X-Ray", "Digital radiography and plain film diagnostic imaging", 1),
        ("CT Scan", "Computed tomography multi-slice diagnostic scans", 1),
        ("MRI", "High-field magnetic resonance imaging scans", 1),
        ("Surgery", "Operating theater suite, chief surgeon, and surgical packages", 1),
        ("Nursing", "24/7 round-the-clock nursing care and vital monitoring", 1),
        ("Emergency", "Triage, emergency trauma bay, and resuscitation tariffs", 1),
        ("Registration", "New patient admission and electronic medical records creation fee", 1),
        ("Other", "Miscellaneous medical consumables, documentation, and auxiliary services", 1)
    ]

    for name, desc, is_act in cost_types_data:
        cursor.execute("SELECT id FROM cost_types WHERE name = ?", (name,))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (name, desc, is_act, now, now))

    conn.commit()

    # 4. Seed Standard Services mapped to Cost Types
    cursor.execute("SELECT COUNT(*) as cnt FROM services")
    if cursor.fetchone()["cnt"] == 0:
        # Fetch cost type IDs
        cursor.execute("SELECT id, name FROM cost_types")
        cost_type_map = {row["name"]: row["id"] for row in cursor.fetchall()}

        services_data = [
            ("SRV-1001", "General Physician Consultation", "Consultation", "Routine OPD medical consultation", 600.0),
            ("SRV-1002", "Senior Specialist Consultation", "Consultation", "Cardiology / Neurology / Orthopedic specialist consultation", 1200.0),
            ("SRV-1003", "Emergency Trauma Consultation", "Emergency", "Immediate emergency doctor resuscitation and assessment", 1500.0),
            ("SRV-1004", "General Inpatient Ward Bed", "Room Charges", "Per day bed charges in general shared ward", 850.0),
            ("SRV-1005", "Semi-Private Room", "Room Charges", "Dual-occupancy semi-private inpatient room per day", 1800.0),
            ("SRV-1006", "Single Private Deluxe Room", "Room Charges", "Single occupancy air-conditioned private room per day", 3500.0),
            ("SRV-1007", "Intensive Care Unit (ICU) Bed", "Room Charges", "Critical care ICU bed with 24/7 monitoring per day", 8500.0),
            ("SRV-1008", "Complete Blood Count (CBC)", "Laboratory Test", "Automated hematology 24-parameter cell count with ESR", 450.0),
            ("SRV-1009", "Comprehensive Metabolic Panel", "Laboratory Test", "Liver, renal, electrolytes, and blood glucose panel", 850.0),
            ("SRV-1010", "Lipid Profile Test", "Laboratory Test", "Cholesterol, triglycerides, HDL, LDL, and VLDL assessment", 650.0),
            ("SRV-1011", "Cardiac Troponin-I Test", "Laboratory Test", "High-sensitivity quantitative troponin-I cardiac biomarker", 1400.0),
            ("SRV-1012", "Digital Chest X-Ray (PA View)", "X-Ray", "High-resolution digital radiography of lungs and thoracic cage", 650.0),
            ("SRV-1013", "CT Scan Abdomen & Pelvis", "CT Scan", "Multi-detector computed tomography scan with contrast", 4500.0),
            ("SRV-1014", "3T MRI Brain Scan", "MRI", "High-field magnetic resonance imaging of brain with contrast", 9500.0),
            ("SRV-1015", "Laparoscopic Surgery Package", "Surgery", "Minimally invasive OT package including anesthesia and surgeon fee", 45000.0),
            ("SRV-1016", "Total Knee Replacement (TKR)", "Surgery", "Orthopedic joint replacement package excluding prosthesis", 120000.0),
            ("SRV-1017", "24/7 Inpatient Nursing Care", "Nursing", "Daily professional nursing care, vitals, and medication administration", 650.0),
            ("SRV-1018", "Metered Medical Oxygen Support", "Other", "High-flow central medical oxygen per hour", 150.0),
            ("SRV-1019", "Mechanical Ventilator Support", "Other", "Continuous invasive mechanical ventilation per hour", 650.0),
            ("SRV-1020", "Augmentin 625mg Tablets (10s)", "Medicine", "Amoxicillin and Potassium Clavulanate strip of 10", 180.0),
            ("SRV-1021", "Rocephin 1g IV Injection", "Medicine", "Ceftriaxone 1g sterile intravenous vial", 320.0),
            ("SRV-1022", "Normal Saline IV Fluid 1000ml", "Medicine", "Sterile isotonic 0.9% Sodium Chloride infusion bottle", 85.0),
            ("SRV-1023", "Hospital Registration Fee", "Registration", "One-time outpatient admission and health record card fee", 150.0)
        ]

        for code, sname, ctype_name, sdesc, sprice in services_data:
            cid = cost_type_map.get(ctype_name, cost_type_map.get("Other"))
            cursor.execute("""
            INSERT INTO services (service_code, service_name, cost_type_id, description, price, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            """, (code, sname, cid, sdesc, sprice, now, now))

    conn.commit()

    # 5. Seed Sample Patients if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM patients")
    if cursor.fetchone()["cnt"] == 0:
        sample_patients = [
            ("PAT-1001", "Sunita Sharma", 42, "FEMALE", "9876543210", "A-402, Lotus Towers, Andheri West, Mumbai", "Dr. Rajesh Verma (Cardiologist)", "ICU-04", today, None),
            ("PAT-1002", "Vikramaditya Rao", 58, "MALE", "9823456781", "12/B, Green Park Colony, Pune", "Dr. Ananya Iyer (Neurologist)", "DLX-204", today, None),
            ("PAT-1003", "Rajesh Patel", 34, "MALE", "9988776655", "Flat 301, Silver Sands, Vashi, Navi Mumbai", "Dr. Amit Kulkarni (General Surgeon)", "SP-108", today, None),
            ("PAT-1004", "Pooja Deshmukh", 29, "FEMALE", "9765432190", "B-15, Royal Palms, Goregaon East, Mumbai", "Dr. Sneha Patil (Physician)", "GW-12", today, None),
            ("PAT-1005", "Mohammed Farooq", 65, "MALE", "9811223344", "78, Crescent Heights, Bandra, Mumbai", "Dr. Rajesh Verma (Cardiologist)", "DLX-208", today, None)
        ]

        for pnum, pname, page, pgender, pphone, paddr, pdoc, proom, padm, pdis in sample_patients:
            cursor.execute("""
            INSERT INTO patients (patient_number, name, age, gender, phone, address, doctor, room_number, admission_date, discharge_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pnum, pname, page, pgender, pphone, paddr, pdoc, proom, padm, pdis, now, now))

    conn.commit()

    # 6. Seed Sample Initial Bills & Payments if empty
    cursor.execute("SELECT COUNT(*) as cnt FROM bills")
    if cursor.fetchone()["cnt"] == 0:
        # Fetch patients
        cursor.execute("SELECT id, patient_number, name FROM patients ORDER BY id ASC")
        patients_list = cursor.fetchall()
        
        # Fetch services
        cursor.execute("""
        SELECT s.id, s.service_code, s.service_name, s.price, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        """)
        services_map = {row["service_code"]: row for row in cursor.fetchall()}

        if len(patients_list) >= 3 and services_map:
            # Sample Bill 1: Sunita Sharma (ICU Care - Paid)
            p1 = patients_list[0]
            items1 = [
                (services_map["SRV-1007"], 3),  # 3 days ICU @ 8500 = 25500
                (services_map["SRV-1011"], 2),  # 2 Troponin @ 1400 = 2800
                (services_map["SRV-1017"], 3),  # 3 Nursing @ 650 = 1950
                (services_map["SRV-1018"], 24), # 24 hrs O2 @ 150 = 3600
                (services_map["SRV-1021"], 4)   # 4 Rocephin @ 320 = 1280
            ]
            subtotal1 = sum(item[0]["price"] * item[1] for item in items1)  # 35130
            discount1 = 1130.0
            taxable1 = subtotal1 - discount1  # 34000
            tax1 = round(taxable1 * 0.05, 2)  # 1700
            total1 = taxable1 + tax1          # 35700
            paid1 = total1
            bal1 = 0.0

            cursor.execute("""
            INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Paid', 'Paid', 'Cardiac emergency ICU stay and medication', ?, ?)
            """, ("BILL-2026-0001", p1["id"], today, subtotal1, discount1, 5.0, tax1, total1, paid1, bal1, now, now))
            bill1_id = cursor.lastrowid

            for srv, qty in items1:
                cursor.execute("""
                INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill1_id, srv["id"], srv["service_name"], srv["cost_type_name"], srv["price"], qty, srv["price"] * qty, now))

            cursor.execute("""
            INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
            VALUES (?, ?, ?, 'UPI', ?, 'UPI/HDFC/9928374610', 'Full payment via hospital QR scanner', ?)
            """, ("REC-2026-0001", bill1_id, paid1, today, now))

            # Sample Bill 2: Vikramaditya Rao (Neurology OPD - Partially Paid)
            p2 = patients_list[1]
            items2 = [
                (services_map["SRV-1002"], 1),  # Specialist Consult @ 1200
                (services_map["SRV-1014"], 1),  # 3T MRI Brain @ 9500
                (services_map["SRV-1008"], 1)   # CBC @ 450
            ]
            subtotal2 = sum(item[0]["price"] * item[1] for item in items2)  # 11150
            discount2 = 150.0
            taxable2 = subtotal2 - discount2  # 11000
            tax2 = round(taxable2 * 0.05, 2)  # 550
            total2 = taxable2 + tax2          # 11550
            paid2 = 5000.0
            bal2 = 6550.0

            cursor.execute("""
            INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Partially Paid', 'Pending', 'Neurology MRI evaluation and blood diagnostics', ?, ?)
            """, ("BILL-2026-0002", p2["id"], today, subtotal2, discount2, 5.0, tax2, total2, paid2, bal2, now, now))
            bill2_id = cursor.lastrowid

            for srv, qty in items2:
                cursor.execute("""
                INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill2_id, srv["id"], srv["service_name"], srv["cost_type_name"], srv["price"], qty, srv["price"] * qty, now))

            cursor.execute("""
            INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
            VALUES (?, ?, ?, 'Card', ?, 'POS-AUTH-773829', 'Initial deposit paid at counter', ?)
            """, ("REC-2026-0002", bill2_id, paid2, today, now))

            # Sample Bill 3: Rajesh Patel (Surgery - Pending)
            p3 = patients_list[2]
            items3 = [
                (services_map["SRV-1015"], 1),  # Laparoscopic Surgery @ 45000
                (services_map["SRV-1005"], 2),  # 2 days Semi-Private @ 1800 = 3600
                (services_map["SRV-1017"], 2)   # 2 days Nursing @ 650 = 1300
            ]
            subtotal3 = sum(item[0]["price"] * item[1] for item in items3)  # 49900
            discount3 = 900.0
            taxable3 = subtotal3 - discount3  # 49000
            tax3 = round(taxable3 * 0.05, 2)  # 2450
            total3 = taxable3 + tax3          # 51450
            paid3 = 0.0
            bal3 = total3

            cursor.execute("""
            INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Pending', 'Elective cholecystectomy admission bill', ?, ?)
            """, ("BILL-2026-0003", p3["id"], today, subtotal3, discount3, 5.0, tax3, total3, paid3, bal3, now, now))
            bill3_id = cursor.lastrowid

            for srv, qty in items3:
                cursor.execute("""
                INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill3_id, srv["id"], srv["service_name"], srv["cost_type_name"], srv["price"], qty, srv["price"] * qty, now))

    conn.commit()


# Initialize database when module is imported
init_database()

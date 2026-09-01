"""
MedBill Enterprise - SQLite Relational Database Engine
Provides ACID-compliant persistent database models, connection management,
schema migrations, and initial hospital seed data for role-based access control (ADMIN, EMPLOYEE, PATIENT).
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

    # 1. Users Table (ADMIN, EMPLOYEE, PATIENT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        full_name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        role TEXT NOT NULL DEFAULT 'ADMIN' CHECK(role IN ('ADMIN', 'EMPLOYEE', 'PATIENT')),
        patient_id INTEGER UNIQUE,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
    )
    """)

    # Safe Schema Migrations for users table
    cursor.execute("PRAGMA table_info(users)")
    cols = [row["name"] for row in cursor.fetchall()]
    if "patient_id" not in cols:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN patient_id INTEGER")
        except Exception as e:
            print("Migration note (patient_id):", e)
    if "phone" not in cols:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        except Exception as e:
            print("Migration note (phone):", e)
    if "is_active" not in cols:
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")
        except Exception as e:
            print("Migration note (is_active):", e)

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
        FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
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
        quantity INTEGER NOT NULL DEFAULT 1 CHECK(quantity > 0),
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

    # Create Performance Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_patient_id ON users(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_number ON patients(patient_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bills_patient_id ON bills(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bills_status ON bills(payment_status, bill_status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bill_items_bill_id ON bill_items(bill_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payments_bill_id ON payments(bill_id)")

    conn.commit()

    # Seed Default Data (Admin, Employee, Cost Types, Services, Settings)
    seed_database(cursor, conn)
    conn.close()


def seed_database(cursor: sqlite3.Cursor, conn: sqlite3.Connection):
    """Seeds default Admin user, default Employee user, hospital settings, cost types, and services catalog."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Seed Default Admin User (admin / admin)
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'admin'")
    if cursor.fetchone()["count"] == 0:
        admin_hash = hash_password("admin")
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, role, is_active, created_at, updated_at)
        VALUES ('admin', ?, 'System Administrator', 'admin@memorialhospital.in', 'ADMIN', 1, ?, ?)
        """, (admin_hash, now, now))

    # 2. Seed Default Employee User (staff / staff123)
    cursor.execute("SELECT COUNT(*) as count FROM users WHERE username = 'staff'")
    if cursor.fetchone()["count"] == 0:
        staff_hash = hash_password("staff123")
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, role, is_active, created_at, updated_at)
        VALUES ('staff', ?, 'Hospital Billing Staff', 'staff@memorialhospital.in', 'EMPLOYEE', 1, ?, ?)
        """, (staff_hash, now, now))

    # 3. Seed Default Hospital Settings
    cursor.execute("SELECT COUNT(*) as count FROM settings")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
        INSERT INTO settings (hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, updated_at)
        VALUES ('Memorial Medical Hospital', '124 Healthcare Avenue, Medical District, Mumbai', '+91 98765 43210', 'billing@memorialhospital.in', 'GSTIN27AAACM1234F1Z5', '₹', 5.0, 'Thank you for choosing Memorial Medical Hospital. Wishing you good health!', ?)
        """, (now,))

    # 4. Seed Standard Cost Types
    cursor.execute("SELECT COUNT(*) as count FROM cost_types")
    if cursor.fetchone()["count"] == 0:
        cost_types_data = [
            ("Consultation", "Doctor OPD and Specialist consultation fees"),
            ("Room Charges", "General Ward, Private, Semi-Private, Deluxe, and ICU bed charges"),
            ("Medicine", "Pharmacy medications, IV fluids, and injectable drugs"),
            ("Laboratory Test", "Pathology, hematology, biochemistry, and microbiology diagnostics"),
            ("X-Ray", "Digital radiography and plain film imaging"),
            ("CT Scan", "Computed Tomography multi-slice diagnostic scans"),
            ("MRI", "Magnetic Resonance Imaging 1.5T and 3T scans"),
            ("Surgery", "Operation Theatre packages, surgeon, anesthesia, and surgical consumables"),
            ("Nursing", "24/7 Inpatient nursing, monitoring, and resident medical care"),
            ("Emergency", "Emergency room triage, resuscitation, and trauma assessment"),
            ("Registration", "Patient admission and registration administration fees"),
            ("Other", "Miscellaneous healthcare supplies, oxygen support, and physiotherapy")
        ]
        for name, desc in cost_types_data:
            cursor.execute("""
            INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
            VALUES (?, ?, 1, ?, ?)
            """, (name, desc, now, now))

    # 5. Seed Standard Medical Services Master Catalog
    cursor.execute("SELECT COUNT(*) as count FROM services")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("SELECT id, name FROM cost_types")
        cost_type_map = {row["name"]: row["id"] for row in cursor.fetchall()}

        services_data = [
            ("SRV-1001", "General Physician Consultation", "Consultation", "Routine OPD doctor consultation and physical examination", 600.0),
            ("SRV-1002", "Senior Specialist Consultation", "Consultation", "Senior Consultant / Super-Specialist examination", 1200.0),
            ("SRV-1003", "Emergency ER Triage Consultation", "Emergency", "Emergency room immediate trauma and resuscitation triage", 1500.0),
            ("SRV-1004", "General Ward Bed (Per Day)", "Room Charges", "Standard general ward admission with nurse call", 950.0),
            ("SRV-1005", "Semi-Private Room (Per Day)", "Room Charges", "Twin-sharing air-conditioned room with TV and sofa", 1800.0),
            ("SRV-1006", "Private Deluxe Room (Per Day)", "Room Charges", "Single private deluxe room with attendant bed and ensuite", 3500.0),
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


# Helper Database Functions for RBAC and Management

def create_employee(username: str, password: str, full_name: str, email: str = "", phone: str = "") -> Dict[str, Any]:
    """Creates a new Employee user account in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    pwd_hash = hash_password(password)

    cursor.execute("""
    INSERT INTO users (username, password_hash, full_name, email, phone, role, is_active, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, 'EMPLOYEE', 1, ?, ?)
    """, (username, pwd_hash, full_name, email, phone, now, now))
    user_id = cursor.lastrowid
    conn.commit()

    cursor.execute("SELECT id, username, full_name, email, phone, role, is_active, created_at FROM users WHERE id = ?", (user_id,))
    emp = dict(cursor.fetchone())
    conn.close()
    return emp


def create_patient_login(patient_id: int, username: str, password: str, email: str = "", full_name: str = "", phone: str = "") -> Dict[str, Any]:
    """Creates a Patient login account securely tied to exactly one patient record."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # Fetch patient
    cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
    pat = cursor.fetchone()
    if not pat:
        conn.close()
        raise ValueError(f"Patient ID {patient_id} does not exist.")

    p_name = full_name or pat["name"]
    p_phone = phone or pat["phone"]
    pwd_hash = hash_password(password)

    # Check if patient already has a login account
    cursor.execute("SELECT id FROM users WHERE patient_id = ?", (patient_id,))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("""
        UPDATE users
        SET username = ?, password_hash = ?, full_name = ?, email = ?, phone = ?, is_active = 1, updated_at = ?
        WHERE id = ?
        """, (username, pwd_hash, p_name, email, p_phone, now, existing["id"]))
        user_id = existing["id"]
    else:
        cursor.execute("""
        INSERT INTO users (username, password_hash, full_name, email, phone, role, patient_id, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'PATIENT', ?, 1, ?, ?)
        """, (username, pwd_hash, p_name, email, p_phone, patient_id, now, now))
        user_id = cursor.lastrowid

    conn.commit()
    cursor.execute("SELECT id, username, full_name, email, role, patient_id, is_active, created_at FROM users WHERE id = ?", (user_id,))
    user_data = dict(cursor.fetchone())
    conn.close()
    return user_data


def get_patient_login_account(patient_id: int) -> Optional[Dict[str, Any]]:
    """Returns the login account for a patient if one exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, phone, is_active, created_at FROM users WHERE patient_id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_employees() -> List[Dict[str, Any]]:
    """Returns list of all employees in the system."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, full_name, email, phone, role, is_active, created_at FROM users WHERE role = 'EMPLOYEE' ORDER BY id DESC")
    employees = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return employees


def toggle_user_status(user_id: int) -> Dict[str, Any]:
    """Toggles active/inactive status for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT id, username, role, is_active FROM users WHERE id = ?", (user_id,))
    u = cursor.fetchone()
    if not u:
        conn.close()
        raise ValueError("User not found.")
    
    if u["role"] == "ADMIN" and u["username"] == "admin":
        conn.close()
        raise ValueError("Master Administrator account cannot be deactivated.")

    new_status = 0 if u["is_active"] == 1 else 1
    cursor.execute("UPDATE users SET is_active = ?, updated_at = ? WHERE id = ?", (new_status, now, user_id))
    conn.commit()
    cursor.execute("SELECT id, username, role, is_active FROM users WHERE id = ?", (user_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    return updated


def reset_user_password(user_id: int, new_password: str) -> bool:
    """Resets the password for a user account."""
    if len(new_password) < 4:
        raise ValueError("Password must be at least 4 characters long.")
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    new_hash = hash_password(new_password)
    cursor.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now, user_id))
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError("User account not found.")
    conn.commit()
    conn.close()
    return True


def reset_to_clean_production_state():
    """Wipes all transactional patient records, bills, bill items, and payments for a clean real-time site."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM payments")
    cursor.execute("DELETE FROM bill_items")
    cursor.execute("DELETE FROM bills")
    cursor.execute("DELETE FROM users WHERE username NOT IN ('admin', 'staff')")
    cursor.execute("UPDATE users SET is_active = 1 WHERE username IN ('admin', 'staff')")
    cursor.execute("DELETE FROM patients")
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('patients', 'bills', 'bill_items', 'payments')")
    except Exception:
        pass
    conn.commit()
    conn.close()


# Initialize database when module is imported
init_database()

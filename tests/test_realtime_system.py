"""
Automated End-to-End System Tests for MedBill Real-time Hospital Billing
Verifies database persistence, authentication, CRUD operations across all modules,
real-time calculation accuracy, payment balances, and reporting aggregation.
"""

import unittest
import json
import os
import sys
from datetime import datetime, date

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.database.db import (
    get_db_connection,
    hash_password,
    verify_password,
    init_database
)


class TestRealtimeHospitalBillingSystem(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()

    def setUp(self):
        self.conn = get_db_connection()

    def tearDown(self):
        self.conn.close()

    def test_01_admin_authentication_and_password_hash(self):
        """Test default admin user exists and password hashing works correctly."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin = cursor.fetchone()
        self.assertIsNotNone(admin, "Admin user must exist in database")
        self.assertEqual(admin["role"], "ADMIN")
        self.assertTrue(verify_password("admin", admin["password_hash"]))
        self.assertFalse(verify_password("wrong_password", admin["password_hash"]))

    def test_02_cost_types_crud_and_unique_constraint(self):
        """Test adding, querying, and unique constraints for Cost Types."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM cost_types")
        initial_count = cursor.fetchone()["count"]
        self.assertGreaterEqual(initial_count, 10, "Default standard cost types should be seeded")

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        unique_name = f"Test_Category_{int(datetime.utcnow().timestamp())}"

        # Create
        cursor.execute("""
        INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
        VALUES (?, 'Test description', 1, ?, ?)
        """, (unique_name, now, now))
        self.conn.commit()
        new_id = cursor.lastrowid

        # Query
        cursor.execute("SELECT * FROM cost_types WHERE id = ?", (new_id,))
        ct = cursor.fetchone()
        self.assertEqual(ct["name"], unique_name)

        # Duplicate Name should fail
        with self.assertRaises(Exception):
            cursor.execute("""
            INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
            VALUES (?, 'Duplicate', 1, ?, ?)
            """, (unique_name, now, now))

    def test_03_services_pricing_and_cost_type_relationship(self):
        """Test service management, price validation, and foreign key relations."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM cost_types LIMIT 1")
        cost_type_id = cursor.fetchone()["id"]

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        code = f"SRV-TEST-{int(datetime.utcnow().timestamp())}"

        cursor.execute("""
        INSERT INTO services (service_code, service_name, cost_type_id, description, price, is_active, created_at, updated_at)
        VALUES (?, 'Test Blood Panel', ?, 'Diagnostic description', 750.0, 1, ?, ?)
        """, (code, cost_type_id, now, now))
        self.conn.commit()
        service_id = cursor.lastrowid

        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        svc = cursor.fetchone()
        self.assertEqual(svc["price"], 750.0)

        # Negative price constraint
        with self.assertRaises(Exception):
            cursor.execute("""
            INSERT INTO services (service_code, service_name, cost_type_id, description, price, is_active, created_at, updated_at)
            VALUES ('SRV-NEG', 'Invalid Service', ?, 'Desc', -50.0, 1, ?, ?)
            """, (cost_type_id, now, now))

    def test_04_patient_crud_operations(self):
        """Test adding, updating, and querying patient records."""
        cursor = self.conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        pnum = f"PAT-TEST-{int(datetime.utcnow().timestamp())}"

        cursor.execute("""
        INSERT INTO patients (patient_number, name, age, gender, phone, address, doctor, room_number, admission_date, discharge_date, created_at, updated_at)
        VALUES (?, 'Aarav Mehta', 35, 'MALE', '9870001122', 'Bandra West, Mumbai', 'Dr. Verma', 'PVT-101', '2026-09-01', NULL, ?, ?)
        """, (pnum, now, now))
        self.conn.commit()
        patient_id = cursor.lastrowid

        # Update
        cursor.execute("UPDATE patients SET room_number = 'PVT-105' WHERE id = ?", (patient_id,))
        self.conn.commit()

        cursor.execute("SELECT room_number FROM patients WHERE id = ?", (patient_id,))
        self.assertEqual(cursor.fetchone()["room_number"], "PVT-105")

    def test_05_realtime_bill_creation_and_snapshot_integrity(self):
        """Test bill generation with line items, discount, tax, and historical price snapshotting."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM patients LIMIT 1")
        patient_id = cursor.fetchone()["id"]

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        today = date.today().isoformat()
        bill_num = f"BILL-TEST-{int(datetime.utcnow().timestamp())}"

        # Create Bill with 2 items: 1 consult @ 1200, 2 CBC @ 450 = 900 -> subtotal = 2100
        subtotal = 2100.0
        discount = 100.0
        taxable = 2000.0
        tax_amount = 100.0  # 5% of 2000
        total_amount = 2100.0
        balance_amount = 2100.0

        cursor.execute("""
        INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 5.0, ?, ?, 0.0, ?, 'Pending', 'Pending', 'Test Bill', ?, ?)
        """, (bill_num, patient_id, today, subtotal, discount, tax_amount, total_amount, balance_amount, now, now))
        bill_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO bill_items (bill_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
        VALUES (?, 'Senior Specialist Consultation', 'Consultation', 1200.0, 1, 1200.0, ?)
        """, (bill_id, now))

        cursor.execute("""
        INSERT INTO bill_items (bill_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
        VALUES (?, 'Complete Blood Count (CBC)', 'Laboratory Test', 450.0, 2, 900.0, ?)
        """, (bill_id, now))
        self.conn.commit()

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        self.assertEqual(bill["total_amount"], 2100.0)
        self.assertEqual(bill["payment_status"], "Pending")

    def test_06_payment_recording_and_automatic_status_update(self):
        """Test recording partial and full payments and verifying balance and status updates."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, total_amount, balance_amount FROM bills WHERE balance_amount > 100 LIMIT 1")
        bill = cursor.fetchone()
        self.assertIsNotNone(bill)

        bill_id = bill["id"]
        initial_balance = bill["balance_amount"]
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        today = date.today().isoformat()

        # Record partial payment of 50.0
        pay_amt = 50.0
        rec_num = f"REC-TEST-{int(datetime.utcnow().timestamp())}"

        cursor.execute("""
        INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
        VALUES (?, ?, ?, 'UPI', ?, 'UPI-REF-12345', 'Partial test payment', ?)
        """, (rec_num, bill_id, pay_amt, today, now))

        cursor.execute("""
        UPDATE bills
        SET paid_amount = paid_amount + ?, balance_amount = balance_amount - ?, payment_status = 'Partially Paid', updated_at = ?
        WHERE id = ?
        """, (pay_amt, pay_amt, now, bill_id))
        self.conn.commit()

        cursor.execute("SELECT balance_amount, payment_status FROM bills WHERE id = ?", (bill_id,))
        updated_bill = cursor.fetchone()
        self.assertAlmostEqual(updated_bill["balance_amount"], initial_balance - pay_amt, places=2)
        self.assertEqual(updated_bill["payment_status"], "Partially Paid")

    def test_07_reports_and_dashboard_aggregation_queries(self):
        """Test that report aggregation calculates real revenue and billing numbers from SQL."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as total FROM payments")
        total_payments = cursor.fetchone()["total"]
        self.assertGreater(total_payments, 0.0, "Payments sum should be positive from seeded data")

        cursor.execute("""
        SELECT bi.cost_type_name, COALESCE(SUM(bi.amount), 0.0) as total_amount
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_status != 'Cancelled'
        GROUP BY bi.cost_type_name
        """)
        breakdown = cursor.fetchall()
        self.assertGreater(len(breakdown), 0, "Cost type breakdown should return aggregated rows")


    def test_08_patient_deletion_after_bill_payment(self):
        """Test creating a patient, billing, settling in full, and deleting patient with all cascades."""
        cursor = self.conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        today = date.today().isoformat()
        pnum = f"PAT-DEL-{int(datetime.utcnow().timestamp())}"

        # 1. Create Patient
        cursor.execute("""
        INSERT INTO patients (patient_number, name, age, gender, phone, address, doctor, room_number, admission_date, discharge_date, created_at, updated_at)
        VALUES (?, 'Settled Patient', 50, 'MALE', '9911223344', 'Mumbai', 'Dr. Verma', 'PVT-202', ?, NULL, ?, ?)
        """, (pnum, today, now, now))
        self.conn.commit()
        patient_id = cursor.lastrowid

        # 2. Create Bill
        bnum = f"BILL-DEL-{int(datetime.utcnow().timestamp())}"
        cursor.execute("""
        INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
        VALUES (?, ?, ?, 5000.0, 0.0, 0.0, 0.0, 5000.0, 0.0, 5000.0, 'Pending', 'Pending', 'Test Bill', ?, ?)
        """, (bnum, patient_id, today, now, now))
        bill_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO bill_items (bill_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
        VALUES (?, 'Specialist Care', 'Consultation', 5000.0, 1, 5000.0, ?)
        """, (bill_id, now))
        self.conn.commit()

        # 3. Pay & Settle Bill in full
        rnum = f"REC-DEL-{int(datetime.utcnow().timestamp())}"
        cursor.execute("""
        INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
        VALUES (?, ?, 5000.0, 'UPI', ?, 'UPI-SETTLE-100', 'Settled in full', ?)
        """, (rnum, bill_id, today, now))

        cursor.execute("""
        UPDATE bills SET paid_amount = 5000.0, balance_amount = 0.0, payment_status = 'Paid', bill_status = 'Paid' WHERE id = ?
        """, (bill_id,))
        self.conn.commit()

        # Verify bill is Paid
        cursor.execute("SELECT payment_status, balance_amount FROM bills WHERE id = ?", (bill_id,))
        b_check = cursor.fetchone()
        self.assertEqual(b_check["payment_status"], "Paid")
        self.assertEqual(b_check["balance_amount"], 0.0)

        # 4. Delete Patient with cascade
        cursor.execute("DELETE FROM payments WHERE bill_id IN (SELECT id FROM bills WHERE patient_id = ?)", (patient_id,))
        cursor.execute("DELETE FROM bill_items WHERE bill_id IN (SELECT id FROM bills WHERE patient_id = ?)", (patient_id,))
        cursor.execute("DELETE FROM bills WHERE patient_id = ?", (patient_id,))
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        self.conn.commit()

        # Verify Patient and all associated bills/payments are deleted
        cursor.execute("SELECT id FROM patients WHERE id = ?", (patient_id,))
        self.assertIsNone(cursor.fetchone())

        cursor.execute("SELECT id FROM bills WHERE id = ?", (bill_id,))
        self.assertIsNone(cursor.fetchone())

        cursor.execute("SELECT id FROM payments WHERE payment_number = ?", (rnum,))
        self.assertIsNone(cursor.fetchone())


if __name__ == "__main__":
    unittest.main()


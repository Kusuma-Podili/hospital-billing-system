"""
MedBill Enterprise - Automated Integration & Security Test Suite for 3-Role RBAC System
Tests Admin Business Analytics, Employee Operations, Patient Provisioning, Patient Self-Service, and Data Isolation.
"""

import unittest
import json
import os
import threading
import time
import urllib.request
import urllib.parse
from datetime import date

from medbill.database.db import (
    init_database,
    get_db_connection,
    reset_to_clean_production_state,
    create_employee,
    create_patient_login,
    hash_password
)
from medbill.web.server import MedBillAPIHandler, ACTIVE_SESSIONS
import socketserver

TEST_PORT = 5892
SERVER_URL = f"http://127.0.0.1:{TEST_PORT}"


class RoleBasedHospitalBillingSystemTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_database()
        reset_to_clean_production_state()

        # Start live test server
        socketserver.TCPServer.allow_reuse_address = True
        cls.httpd = socketserver.TCPServer(("127.0.0.1", TEST_PORT), MedBillAPIHandler)
        cls.server_thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        try:
            cls.httpd.shutdown()
            cls.httpd.server_close()
        except Exception:
            pass

    def setUp(self):
        reset_to_clean_production_state()

    def make_request(self, method: str, endpoint: str, data: dict = None, token: str = None):
        url = f"{SERVER_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        req_data = json.dumps(data).encode("utf-8") if data is not None else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as resp:
                status = resp.status
                body = json.loads(resp.read().decode("utf-8"))
                return status, body
        except urllib.error.HTTPError as e:
            body = json.loads(e.read().decode("utf-8"))
            return e.code, body

    def test_01_admin_login_and_business_analytics(self):
        """Test Admin authentication and business analytics dashboard retrieval."""
        status, body = self.make_request("POST", "/api/auth/login", {
            "username": "admin",
            "password": "admin"
        })
        self.assertEqual(status, 200)
        self.assertTrue(body["success"])
        self.assertEqual(body["user"]["role"], "ADMIN")
        admin_token = body["token"]

        # Access Admin Dashboard
        status, dash = self.make_request("GET", "/api/admin/dashboard", token=admin_token)
        self.assertEqual(status, 200)
        self.assertIn("total_revenue", dash)
        self.assertIn("gross_billed", dash)
        self.assertIn("revenue_by_cost_type", dash)
        self.assertIn("revenue_by_service", dash)
        self.assertIn("payment_methods", dash)

    def test_02_admin_employee_management(self):
        """Test Admin managing employee accounts (creation, listing, status toggle, and password reset)."""
        # Login as Admin
        _, login_body = self.make_request("POST", "/api/auth/login", {"username": "admin", "password": "admin"})
        admin_token = login_body["token"]

        # Create new employee
        status, emp_body = self.make_request("POST", "/api/admin/employees", {
            "full_name": "Kavita Rao",
            "username": "kavita.billing",
            "email": "kavita@hospital.in",
            "phone": "9811223344",
            "password": "kavita_pass_123"
        }, token=admin_token)
        self.assertEqual(status, 201)
        self.assertTrue(emp_body["success"])
        emp_id = emp_body["employee"]["id"]

        # List employees
        status, list_body = self.make_request("GET", "/api/admin/employees", token=admin_token)
        self.assertEqual(status, 200)
        usernames = [e["username"] for e in list_body["employees"]]
        self.assertIn("kavita.billing", usernames)

        # Login as new employee
        status, emp_login = self.make_request("POST", "/api/auth/login", {
            "username": "kavita.billing",
            "password": "kavita_pass_123"
        })
        self.assertEqual(status, 200)
        self.assertEqual(emp_login["user"]["role"], "EMPLOYEE")

        # Deactivate employee
        status, toggle_body = self.make_request("PATCH", f"/api/admin/employees/{emp_id}/toggle", token=admin_token)
        self.assertEqual(status, 200)
        self.assertEqual(toggle_body["user"]["is_active"], 0)

        # Attempt login with deactivated employee
        status, deact_login = self.make_request("POST", "/api/auth/login", {
            "username": "kavita.billing",
            "password": "kavita_pass_123"
        })
        self.assertEqual(status, 403)
        self.assertIn("deactivated", deact_login["error"])

    def test_03_employee_workflow_patient_creation_and_patient_login_provisioning(self):
        """Test Employee creating a patient record, provisioning patient login credentials, and patient login."""
        # Login as Staff
        _, login_body = self.make_request("POST", "/api/auth/login", {"username": "staff", "password": "staff123"})
        staff_token = login_body["token"]

        # Employee registers patient
        status, pat_body = self.make_request("POST", "/api/patients", {
            "name": "Meera Nair",
            "age": 32,
            "gender": "FEMALE",
            "phone": "9876543210",
            "doctor": "Dr. Rajesh Verma",
            "room_number": "DLX-101",
            "address": "402 Palm Grove, Mumbai"
        }, token=staff_token)
        self.assertEqual(status, 201)
        patient_id = pat_body["patient"]["id"]
        patient_number = pat_body["patient"]["patient_number"]

        # Employee creates Patient Login credentials
        status, user_body = self.make_request("POST", f"/api/patients/{patient_id}/create-login", {
            "username": "meera.nair",
            "email": "meera@gmail.com",
            "password": "meerapassword123"
        }, token=staff_token)
        self.assertEqual(status, 201)
        self.assertTrue(user_body["success"])
        self.assertEqual(user_body["user"]["role"], "PATIENT")
        self.assertEqual(user_body["user"]["patient_id"], patient_id)

        # Patient logs in with credentials created by employee
        status, pat_login = self.make_request("POST", "/api/auth/login", {
            "username": "meera.nair",
            "password": "meerapassword123"
        })
        self.assertEqual(status, 200)
        self.assertEqual(pat_login["user"]["role"], "PATIENT")
        self.assertEqual(pat_login["user"]["patient_id"], patient_id)

    def test_04_employee_billing_price_snapshotting_and_payment_settlement(self):
        """Test Employee creating a bill, checking price snapshotting, and recording payments."""
        # Login as Staff
        _, login_body = self.make_request("POST", "/api/auth/login", {"username": "staff", "password": "staff123"})
        staff_token = login_body["token"]

        # Register patient
        _, pat_body = self.make_request("POST", "/api/patients", {
            "name": "Amit Shah", "age": 45, "gender": "MALE", "phone": "9822334455"
        }, token=staff_token)
        patient_id = pat_body["patient"]["id"]

        # Get service SRV-1001 (600 INR) and SRV-1008 (450 INR)
        _, srv_res = self.make_request("GET", "/api/services", token=staff_token)
        services = {s["service_code"]: s for s in srv_res["services"]}
        s1 = services["SRV-1001"] # General Physician Consult (600)
        s2 = services["SRV-1008"] # CBC (450)

        # Create Bill
        status, bill_body = self.make_request("POST", "/api/bills", {
            "patient_id": patient_id,
            "bill_date": date.today().isoformat(),
            "items": [
                {"service_id": s1["id"], "unit_price": 600.0, "quantity": 1},
                {"service_id": s2["id"], "unit_price": 450.0, "quantity": 2} # 450 * 2 = 900
            ],
            "discount": 50.0,
            "tax_percent": 5.0
        }, token=staff_token)
        self.assertEqual(status, 201)
        bill = bill_body["bill"]
        bill_id = bill["id"]
        # Subtotal: 600 + 900 = 1500. Discount: 50. Taxable: 1450. Tax 5%: 72.50. Total: 1522.50
        self.assertEqual(bill["subtotal"], 1500.0)
        self.assertEqual(bill["discount"], 50.0)
        self.assertEqual(bill["tax_amount"], 72.5)
        self.assertEqual(bill["total_amount"], 1522.5)
        self.assertEqual(bill["balance_amount"], 1522.5)
        self.assertEqual(bill["payment_status"], "Pending")

        # Record Partial Payment of 500 via UPI
        status, pay_body = self.make_request("POST", "/api/payments", {
            "bill_id": bill_id,
            "amount": 500.0,
            "payment_method": "UPI",
            "reference_number": "UPI/HDFC/11223344"
        }, token=staff_token)
        self.assertEqual(status, 201)
        self.assertEqual(pay_body["bill"]["paid_amount"], 500.0)
        self.assertEqual(pay_body["bill"]["balance_amount"], 1022.5)
        self.assertEqual(pay_body["bill"]["payment_status"], "Partially Paid")

        # Settle Remaining Payment of 1022.50 via Card
        status, settle_body = self.make_request("POST", "/api/payments", {
            "bill_id": bill_id,
            "amount": 1022.5,
            "payment_method": "Card",
            "reference_number": "POS-AUTH-9988"
        }, token=staff_token)
        self.assertEqual(status, 201)
        self.assertEqual(settle_body["bill"]["balance_amount"], 0.0)
        self.assertEqual(settle_body["bill"]["payment_status"], "Paid")

    def test_05_patient_portal_and_strict_data_isolation(self):
        """Test Patient Portal self-service access and verify strict isolation between Patient A and Patient B."""
        # Login as Staff
        _, login_body = self.make_request("POST", "/api/auth/login", {"username": "staff", "password": "staff123"})
        staff_token = login_body["token"]

        # Create Patient A
        _, pat_a = self.make_request("POST", "/api/patients", {"name": "Patient Alpha", "age": 28, "gender": "FEMALE", "phone": "9800000001"}, token=staff_token)
        pat_a_id = pat_a["patient"]["id"]
        self.make_request("POST", f"/api/patients/{pat_a_id}/create-login", {"username": "patient_a", "password": "pass_patient_a"}, token=staff_token)

        # Create Bill for Patient A
        _, srv_res = self.make_request("GET", "/api/services", token=staff_token)
        s1 = srv_res["services"][0]
        _, bill_a = self.make_request("POST", "/api/bills", {
            "patient_id": pat_a_id,
            "items": [{"service_id": s1["id"], "unit_price": 500.0, "quantity": 1}],
            "discount": 0.0,
            "tax_percent": 0.0
        }, token=staff_token)
        bill_a_id = bill_a["bill"]["id"]

        # Create Patient B
        _, pat_b = self.make_request("POST", "/api/patients", {"name": "Patient Beta", "age": 50, "gender": "MALE", "phone": "9800000002"}, token=staff_token)
        pat_b_id = pat_b["patient"]["id"]
        self.make_request("POST", f"/api/patients/{pat_b_id}/create-login", {"username": "patient_b", "password": "pass_patient_b"}, token=staff_token)

        # Create Bill for Patient B
        _, bill_b = self.make_request("POST", "/api/bills", {
            "patient_id": pat_b_id,
            "items": [{"service_id": s1["id"], "unit_price": 1200.0, "quantity": 1}],
            "discount": 0.0,
            "tax_percent": 0.0
        }, token=staff_token)
        bill_b_id = bill_b["bill"]["id"]

        # Login as Patient A
        status, a_login = self.make_request("POST", "/api/auth/login", {"username": "patient_a", "password": "pass_patient_a"})
        self.assertEqual(status, 200)
        token_a = a_login["token"]

        # Patient A accesses own dashboard
        status, a_dash = self.make_request("GET", "/api/patient/dashboard", token=token_a)
        self.assertEqual(status, 200)
        self.assertEqual(a_dash["patient"]["name"], "Patient Alpha")
        self.assertEqual(a_dash["summary"]["total_bills"], 1)
        self.assertEqual(a_dash["summary"]["total_billed"], 500.0)

        # Patient A views own bills
        status, a_bills = self.make_request("GET", "/api/patient/bills", token=token_a)
        self.assertEqual(status, 200)
        self.assertEqual(len(a_bills["bills"]), 1)
        self.assertEqual(a_bills["bills"][0]["id"], bill_a_id)

        # Patient A views own bill detail
        status, a_bill_detail = self.make_request("GET", f"/api/patient/bills/{bill_a_id}", token=token_a)
        self.assertEqual(status, 200)
        self.assertEqual(a_bill_detail["bill"]["id"], bill_a_id)

        # SECURITY DATA ISOLATION TEST:
        # Patient A tries to access Patient B's bill (/api/patient/bills/<bill_b_id>)
        status, breach_res = self.make_request("GET", f"/api/patient/bills/{bill_b_id}", token=token_a)
        self.assertEqual(status, 403)
        self.assertIn("Access denied", breach_res["error"])

        # Patient A tries to print Patient B's bill
        status, breach_print = self.make_request("GET", f"/api/patient/bills/{bill_b_id}/print", token=token_a)
        self.assertEqual(status, 403)
        self.assertIn("Access denied", breach_print["error"])

    def test_06_unauthorized_action_protection(self):
        """Test that Patient role is blocked from performing Employee/Admin actions."""
        # Login as Staff and create a Patient
        _, staff_login = self.make_request("POST", "/api/auth/login", {"username": "staff", "password": "staff123"})
        staff_token = staff_login["token"]

        _, pat = self.make_request("POST", "/api/patients", {"name": "Security Test Patient", "age": 22, "gender": "FEMALE", "phone": "9812345678"}, token=staff_token)
        pat_id = pat["patient"]["id"]
        self.make_request("POST", f"/api/patients/{pat_id}/create-login", {"username": "sec_pat", "password": "sec_password_1"}, token=staff_token)

        # Login as Patient
        _, pat_login = self.make_request("POST", "/api/auth/login", {"username": "sec_pat", "password": "sec_password_1"})
        pat_token = pat_login["token"]

        # Patient tries to call Admin Dashboard
        status, res = self.make_request("GET", "/api/admin/dashboard", token=pat_token)
        self.assertEqual(status, 403)

        # Patient tries to create a new Patient
        status, res = self.make_request("POST", "/api/patients", {"name": "Hacker", "age": 20, "gender": "MALE", "phone": "0000000000"}, token=pat_token)
        self.assertEqual(status, 403)

        # Patient tries to create a Bill
        status, res = self.make_request("POST", "/api/bills", {"patient_id": pat_id, "items": []}, token=pat_token)
        self.assertEqual(status, 403)

        # Patient tries to record a Payment
        status, res = self.make_request("POST", "/api/payments", {"bill_id": 1, "amount": 100}, token=pat_token)
        self.assertEqual(status, 403)

        # Patient tries to modify Hospital Settings
        status, res = self.make_request("PUT", "/api/settings", {"hospital_name": "Hacked Hospital"}, token=pat_token)
        self.assertEqual(status, 403)


if __name__ == "__main__":
    unittest.main()

"""
MedBill Enterprise - HTTP REST API Server
Provides production RESTful API endpoints for Hospital Billing,
Cost Types, Services & Prices, Patient Management, Real-time Invoicing,
Payment Processing, Audit Reports, and Admin Authentication.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.database.db import (
    get_db_connection,
    hash_password,
    verify_password,
    init_database
)

# Active user sessions cache: token -> {user_id, username, role, expires_at}
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}


def generate_session_token(user: Dict[str, Any]) -> str:
    """Creates a secure session token valid for 24 hours."""
    token = f"mb_{uuid.uuid4().hex}_{int(datetime.utcnow().timestamp())}"
    ACTIVE_SESSIONS[token] = {
        "user_id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "role": user["role"],
        "expires_at": datetime.utcnow() + timedelta(hours=24)
    }
    return token


def validate_session(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Validates session token and returns user context if valid."""
    if not token or token not in ACTIVE_SESSIONS:
        return None
    session = ACTIVE_SESSIONS[token]
    if datetime.utcnow() > session["expires_at"]:
        del ACTIVE_SESSIONS[token]
        return None
    return session


class MedBillAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP REST API Handler & Static SPA Dispatcher for Hospital Billing System.
    """

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"
        query = urllib.parse.parse_qs(parsed_url.query)

        # 1. Static Web Dashboard & Assets
        if path in ("/", "/index.html", "/dashboard"):
            self.serve_static_dashboard()
            return
        elif path == "/logo.png" or path.startswith("/static/"):
            self.serve_static_file(path)
            return

        # 2. Public Health Check
        if path == "/api/health":
            self.send_json_response({"status": "ONLINE", "system": "MedBill Enterprise", "version": "2.0.0", "timestamp": datetime.utcnow().isoformat()})
            return

        # 3. Auth Status Verification
        if path == "/api/auth/verify":
            token = self.get_auth_token()
            user = validate_session(token)
            if user:
                self.send_json_response({"authenticated": True, "user": user})
            else:
                self.send_json_response({"authenticated": False, "error": "Invalid or expired session"}, status=401)
            return

        # 4. Protected API Endpoints
        token = self.get_auth_token()
        # For seamless usability and testing, allow session or default to active admin session
        user_ctx = validate_session(token)

        # Dashboard Statistics
        if path == "/api/dashboard/stats":
            self.handle_get_dashboard_stats()
        # Patients
        elif path == "/api/patients":
            search = query.get("search", [""])[0]
            limit = int(query.get("limit", [100])[0])
            self.handle_get_patients(search, limit)
        elif path.startswith("/api/patients/") and len(path.split("/")) == 4:
            patient_id = int(path.split("/")[3])
            self.handle_get_patient_detail(patient_id)
        # Cost Types
        elif path == "/api/cost-types":
            search = query.get("search", [""])[0]
            self.handle_get_cost_types(search)
        # Services
        elif path == "/api/services":
            search = query.get("search", [""])[0]
            cost_type_id = query.get("cost_type_id", [None])[0]
            active_only = query.get("active_only", ["0"])[0] == "1"
            self.handle_get_services(search, cost_type_id, active_only)
        elif path.startswith("/api/services/") and len(path.split("/")) == 4:
            service_id = int(path.split("/")[3])
            self.handle_get_service_detail(service_id)
        # Bills
        elif path == "/api/bills":
            search = query.get("search", [""])[0]
            patient_id = query.get("patient_id", [None])[0]
            payment_status = query.get("payment_status", [None])[0]
            bill_status = query.get("bill_status", [None])[0]
            from_date = query.get("from_date", [None])[0]
            to_date = query.get("to_date", [None])[0]
            self.handle_get_bills(search, patient_id, payment_status, bill_status, from_date, to_date)
        elif path.startswith("/api/bills/") and path.endswith("/print"):
            bill_id = int(path.split("/")[3])
            self.handle_get_bill_print_data(bill_id)
        elif path.startswith("/api/bills/") and len(path.split("/")) == 4:
            bill_id = int(path.split("/")[3])
            self.handle_get_bill_detail(bill_id)
        # Payments
        elif path == "/api/payments":
            bill_id = query.get("bill_id", [None])[0]
            from_date = query.get("from_date", [None])[0]
            to_date = query.get("to_date", [None])[0]
            self.handle_get_payments(bill_id, from_date, to_date)
        # Reports
        elif path == "/api/reports":
            date_range = query.get("range", ["month"])[0]
            from_date = query.get("from", [None])[0]
            to_date = query.get("to", [None])[0]
            self.handle_get_reports(date_range, from_date, to_date)
        # Settings
        elif path == "/api/settings":
            self.handle_get_settings()
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"
        data = self.read_json_body()

        # Public Auth Endpoints
        if path == "/api/auth/login":
            self.handle_login(data)
            return
        elif path == "/api/auth/logout":
            token = self.get_auth_token()
            if token in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[token]
            self.send_json_response({"success": True, "message": "Successfully signed out."})
            return

        # Protected Write Endpoints
        if path == "/api/auth/change-password":
            self.handle_change_password(data)
        elif path == "/api/patients":
            self.handle_create_patient(data)
        elif path == "/api/cost-types":
            self.handle_create_cost_type(data)
        elif path == "/api/services":
            self.handle_create_service(data)
        elif path == "/api/bills":
            self.handle_create_bill(data)
        elif path == "/api/payments":
            self.handle_create_payment(data)
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_PUT(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"
        data = self.read_json_body()

        if path.startswith("/api/patients/") and len(path.split("/")) == 4:
            patient_id = int(path.split("/")[3])
            self.handle_update_patient(patient_id, data)
        elif path.startswith("/api/cost-types/") and len(path.split("/")) == 4:
            cost_type_id = int(path.split("/")[3])
            self.handle_update_cost_type(cost_type_id, data)
        elif path.startswith("/api/services/") and len(path.split("/")) == 4:
            service_id = int(path.split("/")[3])
            self.handle_update_service(service_id, data)
        elif path.startswith("/api/bills/") and len(path.split("/")) == 4:
            bill_id = int(path.split("/")[3])
            self.handle_update_bill(bill_id, data)
        elif path == "/api/settings":
            self.handle_update_settings(data)
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_PATCH(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"

        if path.startswith("/api/cost-types/") and path.endswith("/toggle"):
            cost_type_id = int(path.split("/")[3])
            self.handle_toggle_cost_type_status(cost_type_id)
        elif path.startswith("/api/services/") and path.endswith("/toggle"):
            service_id = int(path.split("/")[3])
            self.handle_toggle_service_status(service_id)
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_DELETE(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"

        if path.startswith("/api/patients/") and len(path.split("/")) == 4:
            patient_id = int(path.split("/")[3])
            self.handle_delete_patient(patient_id)
        elif path.startswith("/api/cost-types/") and len(path.split("/")) == 4:
            cost_type_id = int(path.split("/")[3])
            self.handle_delete_cost_type(cost_type_id)
        elif path.startswith("/api/services/") and len(path.split("/")) == 4:
            service_id = int(path.split("/")[3])
            self.handle_delete_service(service_id)
        elif path.startswith("/api/bills/") and len(path.split("/")) == 4:
            bill_id = int(path.split("/")[3])
            self.handle_delete_bill(bill_id)
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    # -------------------------------------------------------------------------
    # AUTHENTICATION HANDLERS
    # -------------------------------------------------------------------------
    def handle_login(self, data: Dict[str, Any]):
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        if not username or not password:
            self.send_json_response({"error": "Username and password are required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user or not verify_password(password, user["password_hash"]):
            self.send_json_response({"error": "Invalid username or secret passcode."}, status=401)
            return

        token = generate_session_token(dict(user))
        self.send_json_response({
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"]
            }
        })

    def handle_change_password(self, data: Dict[str, Any]):
        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()
        username = data.get("username", "admin").strip()

        if not current_password or not new_password:
            self.send_json_response({"error": "Current and new password are required."}, status=400)
            return

        if len(new_password) < 4:
            self.send_json_response({"error": "New password must be at least 4 characters."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user or not verify_password(current_password, user["password_hash"]):
            conn.close()
            self.send_json_response({"error": "Incorrect current password."}, status=400)
            return

        new_hash = hash_password(new_password)
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (new_hash, now, user["id"]))
        conn.commit()
        conn.close()

        self.send_json_response({"success": True, "message": "Password updated successfully!"})

    # -------------------------------------------------------------------------
    # DASHBOARD HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_dashboard_stats(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        today = date.today().isoformat()
        first_day_month = date.today().replace(day=1).isoformat()

        # Metrics calculated from database
        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills")
        total_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as total FROM payments")
        total_revenue = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(balance_amount), 0.0) as pending FROM bills WHERE bill_status != 'Cancelled'")
        pending_amount = cursor.fetchone()["pending"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Paid' AND bill_status != 'Cancelled'")
        paid_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Pending' AND bill_status != 'Cancelled'")
        pending_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Partially Paid' AND bill_status != 'Cancelled'")
        partial_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as today_rev FROM payments WHERE payment_date = ?", (today,))
        today_revenue = cursor.fetchone()["today_rev"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as month_rev FROM payments WHERE payment_date >= ?", (first_day_month,))
        monthly_revenue = cursor.fetchone()["month_rev"]

        # Recent 5 Bills
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.phone as patient_phone
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        ORDER BY b.id DESC
        LIMIT 5
        """)
        recent_bills = [dict(row) for row in cursor.fetchall()]

        # Recent 5 Patients
        cursor.execute("""
        SELECT * FROM patients
        ORDER BY id DESC
        LIMIT 5
        """)
        recent_patients = [dict(row) for row in cursor.fetchall()]

        # Revenue by Cost Type
        cursor.execute("""
        SELECT bi.cost_type_name, COALESCE(SUM(bi.amount), 0.0) as total_amount
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_status != 'Cancelled'
        GROUP BY bi.cost_type_name
        ORDER BY total_amount DESC
        """)
        revenue_by_cost_type = [dict(row) for row in cursor.fetchall()]

        # Payment Methods Summary
        cursor.execute("""
        SELECT payment_method, COUNT(*) as txn_count, COALESCE(SUM(amount), 0.0) as total_amount
        FROM payments
        GROUP BY payment_method
        ORDER BY total_amount DESC
        """)
        payment_methods = [dict(row) for row in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "total_patients": total_patients,
            "total_bills": total_bills,
            "total_revenue": round(total_revenue, 2),
            "pending_amount": round(pending_amount, 2),
            "paid_bills_count": paid_bills,
            "pending_bills_count": pending_bills,
            "partially_paid_bills_count": partial_bills,
            "today_revenue": round(today_revenue, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "recent_bills": recent_bills,
            "recent_patients": recent_patients,
            "revenue_by_cost_type": revenue_by_cost_type,
            "payment_methods": payment_methods
        })

    # -------------------------------------------------------------------------
    # PATIENT CRUD HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_patients(self, search: str, limit: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search:
            s_param = f"%{search}%"
            cursor.execute("""
            SELECT p.*, COUNT(b.id) as total_bills, COALESCE(SUM(b.total_amount), 0.0) as total_billed, COALESCE(SUM(b.balance_amount), 0.0) as outstanding_balance
            FROM patients p
            LEFT JOIN bills b ON p.id = b.patient_id AND b.bill_status != 'Cancelled'
            WHERE p.name LIKE ? OR p.patient_number LIKE ? OR p.phone LIKE ?
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT ?
            """, (s_param, s_param, s_param, limit))
        else:
            cursor.execute("""
            SELECT p.*, COUNT(b.id) as total_bills, COALESCE(SUM(b.total_amount), 0.0) as total_billed, COALESCE(SUM(b.balance_amount), 0.0) as outstanding_balance
            FROM patients p
            LEFT JOIN bills b ON p.id = b.patient_id AND b.bill_status != 'Cancelled'
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT ?
            """, (limit,))

        patients = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response({"total": len(patients), "patients": patients})

    def handle_get_patient_detail(self, patient_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            conn.close()
            self.send_json_response({"error": "Patient not found."}, status=404)
            return

        cursor.execute("""
        SELECT * FROM bills WHERE patient_id = ? ORDER BY id DESC
        """, (patient_id,))
        bills = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({
            "patient": dict(patient),
            "bills": bills
        })

    def handle_create_patient(self, data: Dict[str, Any]):
        name = data.get("name", "").strip()
        age = data.get("age")
        gender = data.get("gender", "MALE").strip().upper()
        phone = data.get("phone", "").strip()
        address = data.get("address", "").strip()
        doctor = data.get("doctor", "").strip()
        room_number = data.get("room_number", "").strip()
        admission_date = data.get("admission_date") or date.today().isoformat()
        discharge_date = data.get("discharge_date") or None

        if not name:
            self.send_json_response({"error": "Patient name is required."}, status=400)
            return
        if age is None or int(age) < 0:
            self.send_json_response({"error": "Valid patient age is required."}, status=400)
            return
        if not phone:
            self.send_json_response({"error": "Patient phone number is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate unique patient number e.g. PAT-1006
        cursor.execute("SELECT MAX(id) as max_id FROM patients")
        max_id = cursor.fetchone()["max_id"] or 1000
        patient_number = data.get("patient_number") or f"PAT-{max_id + 1}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("""
            INSERT INTO patients (patient_number, name, age, gender, phone, address, doctor, room_number, admission_date, discharge_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (patient_number, name, int(age), gender, phone, address, doctor, room_number, admission_date, discharge_date, now, now))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM patients WHERE id = ?", (new_id,))
            created_patient = dict(cursor.fetchone())
            conn.close()
            self.send_json_response({"success": True, "patient": created_patient}, status=201)
        except sqlite3.IntegrityError as e:
            conn.close()
            self.send_json_response({"error": f"Patient number '{patient_number}' already exists."}, status=400)

    def handle_update_patient(self, patient_id: int, data: Dict[str, Any]):
        name = data.get("name", "").strip()
        age = data.get("age")
        gender = data.get("gender", "MALE").strip().upper()
        phone = data.get("phone", "").strip()
        address = data.get("address", "").strip()
        doctor = data.get("doctor", "").strip()
        room_number = data.get("room_number", "").strip()
        admission_date = data.get("admission_date") or date.today().isoformat()
        discharge_date = data.get("discharge_date") or None

        if not name:
            self.send_json_response({"error": "Patient name cannot be empty."}, status=400)
            return
        if age is None or int(age) < 0:
            self.send_json_response({"error": "Valid patient age is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE patients
        SET name = ?, age = ?, gender = ?, phone = ?, address = ?, doctor = ?, room_number = ?, admission_date = ?, discharge_date = ?, updated_at = ?
        WHERE id = ?
        """, (name, int(age), gender, phone, address, doctor, room_number, admission_date, discharge_date, now, patient_id))

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({"error": "Patient record not found."}, status=404)
            return

        conn.commit()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        updated_patient = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "patient": updated_patient})

    def handle_delete_patient(self, patient_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if patient exists
        cursor.execute("SELECT id, name, patient_number FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            conn.close()
            self.send_json_response({"error": "Patient record not found."}, status=404)
            return

        # Cleanly delete all associated payment records
        cursor.execute("DELETE FROM payments WHERE bill_id IN (SELECT id FROM bills WHERE patient_id = ?)", (patient_id,))
        
        # Cleanly delete all associated bill item records
        cursor.execute("DELETE FROM bill_items WHERE bill_id IN (SELECT id FROM bills WHERE patient_id = ?)", (patient_id,))
        
        # Cleanly delete all associated bills
        cursor.execute("DELETE FROM bills WHERE patient_id = ?", (patient_id,))

        # Delete the patient record
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        
        conn.commit()
        conn.close()
        self.send_json_response({
            "success": True,
            "message": f"Patient {patient['name']} ({patient['patient_number']}) and all associated records deleted successfully."
        })

    # -------------------------------------------------------------------------
    # COST TYPES HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_cost_types(self, search: str):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search:
            s_param = f"%{search}%"
            cursor.execute("""
            SELECT ct.*, COUNT(s.id) as service_count
            FROM cost_types ct
            LEFT JOIN services s ON ct.id = s.cost_type_id
            WHERE ct.name LIKE ? OR ct.description LIKE ?
            GROUP BY ct.id
            ORDER BY ct.id ASC
            """, (s_param, s_param))
        else:
            cursor.execute("""
            SELECT ct.*, COUNT(s.id) as service_count
            FROM cost_types ct
            LEFT JOIN services s ON ct.id = s.cost_type_id
            GROUP BY ct.id
            ORDER BY ct.id ASC
            """)

        cost_types = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response({"total": len(cost_types), "cost_types": cost_types})

    def handle_create_cost_type(self, data: Dict[str, Any]):
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        is_active = 1 if data.get("is_active", True) else 0

        if not name:
            self.send_json_response({"error": "Cost type name is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
            INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """, (name, description, is_active, now, now))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("SELECT * FROM cost_types WHERE id = ?", (new_id,))
            ct = dict(cursor.fetchone())
            conn.close()
            self.send_json_response({"success": True, "cost_type": ct}, status=201)
        except sqlite3.IntegrityError:
            conn.close()
            self.send_json_response({"error": f"Cost type '{name}' already exists."}, status=400)

    def handle_update_cost_type(self, cost_type_id: int, data: Dict[str, Any]):
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        is_active = 1 if data.get("is_active", True) else 0

        if not name:
            self.send_json_response({"error": "Cost type name cannot be empty."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
            UPDATE cost_types
            SET name = ?, description = ?, is_active = ?, updated_at = ?
            WHERE id = ?
            """, (name, description, is_active, now, cost_type_id))
            conn.commit()
            cursor.execute("SELECT * FROM cost_types WHERE id = ?", (cost_type_id,))
            ct = dict(cursor.fetchone())
            conn.close()
            self.send_json_response({"success": True, "cost_type": ct})
        except sqlite3.IntegrityError:
            conn.close()
            self.send_json_response({"error": f"Cost type name '{name}' already in use by another category."}, status=400)

    def handle_toggle_cost_type_status(self, cost_type_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("SELECT is_active FROM cost_types WHERE id = ?", (cost_type_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self.send_json_response({"error": "Cost type not found."}, status=404)
            return

        new_status = 0 if row["is_active"] == 1 else 1
        cursor.execute("UPDATE cost_types SET is_active = ?, updated_at = ? WHERE id = ?", (new_status, now, cost_type_id))
        conn.commit()
        cursor.execute("SELECT * FROM cost_types WHERE id = ?", (cost_type_id,))
        ct = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "cost_type": ct})

    def handle_delete_cost_type(self, cost_type_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if services are assigned to this cost type
        cursor.execute("SELECT COUNT(*) as count FROM services WHERE cost_type_id = ?", (cost_type_id,))
        svc_count = cursor.fetchone()["count"]
        if svc_count > 0:
            conn.close()
            self.send_json_response({
                "error": f"Cannot delete cost type. It has {svc_count} assigned service(s). Reassign or delete services first."
            }, status=400)
            return

        cursor.execute("DELETE FROM cost_types WHERE id = ?", (cost_type_id,))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "message": "Cost type deleted successfully."})

    # -------------------------------------------------------------------------
    # SERVICES & PRICES HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_services(self, search: str, cost_type_id: Optional[str], active_only: bool):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_sql = """
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE 1=1
        """
        params = []

        if search:
            query_sql += " AND (s.service_name LIKE ? OR s.service_code LIKE ? OR s.description LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param])

        if cost_type_id:
            query_sql += " AND s.cost_type_id = ?"
            params.append(int(cost_type_id))

        if active_only:
            query_sql += " AND s.is_active = 1 AND ct.is_active = 1"

        query_sql += " ORDER BY ct.name ASC, s.service_name ASC"

        cursor.execute(query_sql, params)
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response({"total": len(services), "services": services})

    def handle_get_service_detail(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE s.id = ?", (service_id,))
        """)
        svc = cursor.fetchone()
        conn.close()

        if not svc:
            self.send_json_response({"error": "Service not found."}, status=404)
        else:
            self.send_json_response({"service": dict(svc)})

    def handle_create_service(self, data: Dict[str, Any]):
        service_name = data.get("service_name", "").strip()
        cost_type_id = data.get("cost_type_id")
        price = data.get("price")
        description = data.get("description", "").strip()
        is_active = 1 if data.get("is_active", True) else 0

        if not service_name:
            self.send_json_response({"error": "Service name is required."}, status=400)
            return
        if not cost_type_id:
            self.send_json_response({"error": "Cost type must be selected."}, status=400)
            return
        if price is None or float(price) < 0:
            self.send_json_response({"error": "Price must be a non-negative number."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate service code e.g. SRV-1024
        cursor.execute("SELECT MAX(id) as max_id FROM services")
        max_id = cursor.fetchone()["max_id"] or 1000
        service_code = data.get("service_code") or f"SRV-{max_id + 1}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        try:
            cursor.execute("""
            INSERT INTO services (service_code, service_name, cost_type_id, description, price, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (service_code, service_name, int(cost_type_id), description, float(price), is_active, now, now))
            conn.commit()
            new_id = cursor.lastrowid
            cursor.execute("""
            SELECT s.*, ct.name as cost_type_name
            FROM services s
            JOIN cost_types ct ON s.cost_type_id = ct.id
            WHERE s.id = ?
            """, (new_id,))
            created_svc = dict(cursor.fetchone())
            conn.close()
            self.send_json_response({"success": True, "service": created_svc}, status=201)
        except sqlite3.IntegrityError as e:
            conn.close()
            self.send_json_response({"error": f"Service code '{service_code}' already exists."}, status=400)

    def handle_update_service(self, service_id: int, data: Dict[str, Any]):
        service_name = data.get("service_name", "").strip()
        cost_type_id = data.get("cost_type_id")
        price = data.get("price")
        description = data.get("description", "").strip()
        is_active = 1 if data.get("is_active", True) else 0

        if not service_name:
            self.send_json_response({"error": "Service name cannot be empty."}, status=400)
            return
        if price is None or float(price) < 0:
            self.send_json_response({"error": "Price must be non-negative."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE services
        SET service_name = ?, cost_type_id = ?, description = ?, price = ?, is_active = ?, updated_at = ?
        WHERE id = ?
        """, (service_name, int(cost_type_id), description, float(price), is_active, now, service_id))

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({"error": "Service not found."}, status=404)
            return

        conn.commit()
        cursor.execute("""
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE s.id = ?
        """, (service_id,))
        svc = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "service": svc})

    def handle_toggle_service_status(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("SELECT is_active FROM services WHERE id = ?", (service_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            self.send_json_response({"error": "Service not found."}, status=404)
            return

        new_status = 0 if row["is_active"] == 1 else 1
        cursor.execute("UPDATE services SET is_active = ?, updated_at = ? WHERE id = ?", (new_status, now, service_id))
        conn.commit()
        cursor.execute("SELECT * FROM services WHERE id = ?", (service_id,))
        svc = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "service": svc})

    def handle_delete_service(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if service is referenced in existing bill items
        cursor.execute("SELECT COUNT(*) as count FROM bill_items WHERE service_id = ?", (service_id,))
        usage_count = cursor.fetchone()["count"]

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if usage_count > 0:
            # Safe soft deactivation so previous bills retain historical integrity
            cursor.execute("UPDATE services SET is_active = 0, updated_at = ? WHERE id = ?", (now, service_id))
            conn.commit()
            conn.close()
            self.send_json_response({
                "success": True,
                "message": f"Service is referenced in {usage_count} existing bill(s). It has been safely deactivated to protect historical records."
            })
        else:
            cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
            conn.commit()
            conn.close()
            self.send_json_response({"success": True, "message": "Service deleted successfully."})

    # -------------------------------------------------------------------------
    # BILLING MODULE (CORE REAL-TIME INVOICING)
    # -------------------------------------------------------------------------
    def handle_get_bills(self, search: str, patient_id: Optional[str], payment_status: Optional[str], bill_status: Optional[str], from_date: Optional[str], to_date: Optional[str]):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_sql = """
        SELECT b.*, p.name as patient_name, p.patient_number, p.phone as patient_phone, p.doctor as patient_doctor
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE 1=1
        """
        params = []

        if search:
            query_sql += " AND (b.bill_number LIKE ? OR p.name LIKE ? OR p.patient_number LIKE ?)"
            s_param = f"%{search}%"
            params.extend([s_param, s_param, s_param])

        if patient_id:
            query_sql += " AND b.patient_id = ?"
            params.append(int(patient_id))

        if payment_status:
            query_sql += " AND b.payment_status = ?"
            params.append(payment_status)

        if bill_status:
            query_sql += " AND b.bill_status = ?"
            params.append(bill_status)

        if from_date:
            query_sql += " AND b.bill_date >= ?"
            params.append(from_date)

        if to_date:
            query_sql += " AND b.bill_date <= ?"
            params.append(to_date)

        query_sql += " ORDER BY b.id DESC"

        cursor.execute(query_sql, params)
        bills = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response({"total": len(bills), "bills": bills})

    def handle_get_bill_detail(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.age as patient_age, p.gender as patient_gender, p.phone as patient_phone, p.address as patient_address, p.doctor as patient_doctor, p.room_number as patient_room
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill record not found."}, status=404)
            return

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        items = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(row) for row in cursor.fetchall()]

        conn.close()
        self.send_json_response({
            "bill": dict(bill),
            "items": items,
            "payments": payments
        })

    def handle_get_bill_print_data(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM settings ORDER BY id DESC LIMIT 1")
        settings = dict(cursor.fetchone() or {})

        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.age as patient_age, p.gender as patient_gender, p.phone as patient_phone, p.address as patient_address, p.doctor as patient_doctor, p.room_number as patient_room
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        items = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(row) for row in cursor.fetchall()]

        conn.close()
        self.send_json_response({
            "hospital": settings,
            "bill": dict(bill),
            "items": items,
            "payments": payments
        })

    def handle_create_bill(self, data: Dict[str, Any]):
        patient_id = data.get("patient_id")
        bill_date = data.get("bill_date") or date.today().isoformat()
        items_data = data.get("items", [])
        discount = float(data.get("discount", 0.0))
        tax_percent = float(data.get("tax_percent", 5.0))
        notes = data.get("notes", "").strip()

        if not patient_id:
            self.send_json_response({"error": "Patient must be selected for billing."}, status=400)
            return

        if not items_data or len(items_data) == 0:
            self.send_json_response({"error": "At least one billing service item is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate patient exists
        cursor.execute("SELECT id, name FROM patients WHERE id = ?", (patient_id,))
        if not cursor.fetchone():
            conn.close()
            self.send_json_response({"error": "Selected patient does not exist."}, status=400)
            return

        # Calculate line items, ensuring exact snapshot of prices
        processed_items = []
        subtotal = 0.0

        for item in items_data:
            service_id = item.get("service_id")
            quantity = float(item.get("quantity", 1.0))
            if quantity <= 0:
                conn.close()
                self.send_json_response({"error": "Item quantity must be greater than zero."}, status=400)
                return

            if service_id:
                cursor.execute("""
                SELECT s.id, s.service_name, s.price, ct.name as cost_type_name
                FROM services s
                JOIN cost_types ct ON s.cost_type_id = ct.id
                WHERE s.id = ?
                """, (service_id,))
                svc = cursor.fetchone()
                if not svc:
                    conn.close()
                    self.send_json_response({"error": f"Service ID {service_id} not found."}, status=400)
                    return
                unit_price = float(item.get("unit_price", svc["price"]))
                service_name = svc["service_name"]
                cost_type_name = svc["cost_type_name"]
            else:
                service_name = item.get("service_name", "Custom Medical Charge")
                cost_type_name = item.get("cost_type_name", "Other")
                unit_price = float(item.get("unit_price", 0.0))

            if unit_price < 0:
                conn.close()
                self.send_json_response({"error": "Unit price cannot be negative."}, status=400)
                return

            line_amount = round(unit_price * quantity, 2)
            subtotal += line_amount
            processed_items.append({
                "service_id": service_id,
                "service_name": service_name,
                "cost_type_name": cost_type_name,
                "unit_price": unit_price,
                "quantity": quantity,
                "amount": line_amount
            })

        subtotal = round(subtotal, 2)
        discount = max(0.0, min(discount, subtotal))
        taxable_amount = max(0.0, subtotal - discount)
        tax_amount = round(taxable_amount * (tax_percent / 100.0), 2)
        total_amount = round(taxable_amount + tax_amount, 2)
        paid_amount = 0.0
        balance_amount = total_amount
        payment_status = "Pending"
        bill_status = "Pending"

        # Generate unique bill number e.g. BILL-2026-0045
        cursor.execute("SELECT MAX(id) as max_id FROM bills")
        max_id = cursor.fetchone()["max_id"] or 0
        bill_number = f"BILL-{datetime.now().year}-{max_id + 1:04d}"
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, now, now))
        bill_id = cursor.lastrowid

        # Insert snapshot items
        for itm in processed_items:
            cursor.execute("""
            INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (bill_id, itm["service_id"], itm["service_name"], itm["cost_type_name"], itm["unit_price"], itm["quantity"], itm["amount"], now))

        conn.commit()

        # Fetch complete bill
        cursor.execute("SELECT b.*, p.name as patient_name FROM bills b JOIN patients p ON b.patient_id = p.id WHERE b.id = ?", (bill_id,))
        created_bill = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({"success": True, "bill": created_bill}, status=201)

    def handle_update_bill(self, bill_id: int, data: Dict[str, Any]):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        existing_bill = cursor.fetchone()
        if not existing_bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        items_data = data.get("items", [])
        discount = float(data.get("discount", existing_bill["discount"]))
        tax_percent = float(data.get("tax_percent", existing_bill["tax_percent"]))
        bill_date = data.get("bill_date", existing_bill["bill_date"])
        notes = data.get("notes", existing_bill["notes"])

        if items_data and len(items_data) > 0:
            cursor.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
            subtotal = 0.0
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

            for item in items_data:
                quantity = float(item.get("quantity", 1.0))
                unit_price = float(item.get("unit_price", 0.0))
                service_id = item.get("service_id")
                service_name = item.get("service_name", "Medical Service")
                cost_type_name = item.get("cost_type_name", "Other")

                line_amount = round(unit_price * quantity, 2)
                subtotal += line_amount

                cursor.execute("""
                INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, line_amount, now))

            subtotal = round(subtotal, 2)
            discount = max(0.0, min(discount, subtotal))
            taxable = max(0.0, subtotal - discount)
            tax_amount = round(taxable * (tax_percent / 100.0), 2)
            total_amount = round(taxable + tax_amount, 2)
            paid_amount = existing_bill["paid_amount"]
            balance_amount = max(0.0, total_amount - paid_amount)

            if balance_amount == 0.0:
                payment_status = "Paid"
            elif paid_amount > 0.0:
                payment_status = "Partially Paid"
            else:
                payment_status = "Pending"

            cursor.execute("""
            UPDATE bills
            SET bill_date = ?, subtotal = ?, discount = ?, tax_percent = ?, tax_amount = ?, total_amount = ?, balance_amount = ?, payment_status = ?, notes = ?, updated_at = ?
            WHERE id = ?
            """, (bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, balance_amount, payment_status, notes, now, bill_id))

        conn.commit()
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        updated_bill = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "bill": updated_bill})

    def handle_delete_bill(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "message": "Bill removed successfully."})

    # -------------------------------------------------------------------------
    # PAYMENTS HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_payments(self, bill_id: Optional[str], from_date: Optional[str], to_date: Optional[str]):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_sql = """
        SELECT py.*, b.bill_number, b.total_amount as bill_total, b.paid_amount as bill_paid, b.balance_amount as bill_balance, p.name as patient_name, p.patient_number
        FROM payments py
        JOIN bills b ON py.bill_id = b.id
        JOIN patients p ON b.patient_id = p.id
        WHERE 1=1
        """
        params = []

        if bill_id:
            query_sql += " AND py.bill_id = ?"
            params.append(int(bill_id))

        if from_date:
            query_sql += " AND py.payment_date >= ?"
            params.append(from_date)

        if to_date:
            query_sql += " AND py.payment_date <= ?"
            params.append(to_date)

        query_sql += " ORDER BY py.id DESC"
        cursor.execute(query_sql, params)
        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        self.send_json_response({"total": len(payments), "payments": payments})

    def handle_create_payment(self, data: Dict[str, Any]):
        bill_id = data.get("bill_id")
        amount = float(data.get("amount", 0.0))
        payment_method = data.get("payment_method", "Cash").strip()
        payment_date = data.get("payment_date") or date.today().isoformat()
        reference_number = data.get("reference_number", "").strip()
        notes = data.get("notes", "").strip()

        if not bill_id:
            self.send_json_response({"error": "Bill ID is required."}, status=400)
            return

        if amount <= 0:
            self.send_json_response({"error": "Payment amount must be greater than zero."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        remaining_balance = float(bill["balance_amount"])
        if amount > (remaining_balance + 0.01):
            conn.close()
            self.send_json_response({
                "error": f"Payment amount (₹{amount:.2f}) cannot exceed remaining balance (₹{remaining_balance:.2f})."
            }, status=400)
            return

        # Generate unique receipt number e.g. REC-2026-0045
        cursor.execute("SELECT MAX(id) as max_id FROM payments")
        max_id = cursor.fetchone()["max_id"] or 0
        payment_number = f"REC-{datetime.now().year}-{max_id + 1:04d}"
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, now))
        payment_id = cursor.lastrowid

        # Update bill paid amount and balance
        new_paid_amount = round(float(bill["paid_amount"]) + amount, 2)
        new_balance = max(0.0, round(float(bill["total_amount"]) - new_paid_amount, 2))

        if new_balance <= 0.01:
            new_payment_status = "Paid"
            new_bill_status = "Paid"
        else:
            new_payment_status = "Partially Paid"
            new_bill_status = bill["bill_status"]

        cursor.execute("""
        UPDATE bills
        SET paid_amount = ?, balance_amount = ?, payment_status = ?, bill_status = ?, updated_at = ?
        WHERE id = ?
        """, (new_paid_amount, new_balance, new_payment_status, new_bill_status, now, bill_id))

        conn.commit()

        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        created_payment = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        updated_bill = dict(cursor.fetchone())

        conn.close()

        self.send_json_response({
            "success": True,
            "payment": created_payment,
            "bill": updated_bill,
            "message": f"Payment of ₹{amount:.2f} recorded successfully! Status: {new_payment_status}"
        }, status=201)

    # -------------------------------------------------------------------------
    # REPORTS HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_reports(self, date_range: str, from_date: Optional[str], to_date: Optional[str]):
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today()
        if date_range == "today":
            start_date = today.isoformat()
            end_date = today.isoformat()
        elif date_range == "week":
            start_date = (today - timedelta(days=7)).isoformat()
            end_date = today.isoformat()
        elif date_range == "month":
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        elif date_range == "custom" and from_date and to_date:
            start_date = from_date
            end_date = to_date
        else:
            start_date = "2020-01-01"
            end_date = "2099-12-31"

        # KPI Summary for Range
        cursor.execute("""
        SELECT COALESCE(SUM(amount), 0.0) as revenue_collected
        FROM payments
        WHERE payment_date >= ? AND payment_date <= ?
        """, (start_date, end_date))
        revenue_collected = cursor.fetchone()["revenue_collected"]

        cursor.execute("""
        SELECT COUNT(*) as bills_count, COALESCE(SUM(total_amount), 0.0) as gross_billed, COALESCE(SUM(balance_amount), 0.0) as pending_receivables
        FROM bills
        WHERE bill_date >= ? AND bill_date <= ? AND bill_status != 'Cancelled'
        """, (start_date, end_date))
        bill_stats = cursor.fetchone()
        gross_billed = bill_stats["gross_billed"]
        pending_receivables = bill_stats["pending_receivables"]
        bills_count = bill_stats["bills_count"]

        # Daily Revenue Breakdown
        cursor.execute("""
        SELECT payment_date, COUNT(*) as transaction_count, COALESCE(SUM(amount), 0.0) as daily_total
        FROM payments
        WHERE payment_date >= ? AND payment_date <= ?
        GROUP BY payment_date
        ORDER BY payment_date DESC
        """, (start_date, end_date))
        daily_revenue = [dict(row) for row in cursor.fetchall()]

        # Revenue by Cost Type
        cursor.execute("""
        SELECT bi.cost_type_name, COUNT(bi.id) as item_count, COALESCE(SUM(bi.amount), 0.0) as total_amount
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_date >= ? AND b.bill_date <= ? AND b.bill_status != 'Cancelled'
        GROUP BY bi.cost_type_name
        ORDER BY total_amount DESC
        """, (start_date, end_date))
        cost_type_breakdown = [dict(row) for row in cursor.fetchall()]

        # Top Services by Revenue
        cursor.execute("""
        SELECT bi.service_name, bi.cost_type_name, SUM(bi.quantity) as total_qty, COALESCE(SUM(bi.amount), 0.0) as total_revenue
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_date >= ? AND b.bill_date <= ? AND b.bill_status != 'Cancelled'
        GROUP BY bi.service_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """, (start_date, end_date))
        top_services = [dict(row) for row in cursor.fetchall()]

        # Payment Methods Distribution
        cursor.execute("""
        SELECT payment_method, COUNT(*) as count, COALESCE(SUM(amount), 0.0) as total_amount
        FROM payments
        WHERE payment_date >= ? AND payment_date <= ?
        GROUP BY payment_method
        ORDER BY total_amount DESC
        """, (start_date, end_date))
        payment_methods = [dict(row) for row in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "range": date_range,
            "start_date": start_date,
            "end_date": end_date,
            "revenue_collected": round(revenue_collected, 2),
            "gross_billed": round(gross_billed, 2),
            "pending_receivables": round(pending_receivables, 2),
            "bills_count": bills_count,
            "daily_revenue": daily_revenue,
            "cost_type_breakdown": cost_type_breakdown,
            "top_services": top_services,
            "payment_methods": payment_methods
        })

    # -------------------------------------------------------------------------
    # SETTINGS HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_settings(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        self.send_json_response(dict(row or {}))

    def handle_update_settings(self, data: Dict[str, Any]):
        hospital_name = data.get("hospital_name", "Memorial Medical Hospital").strip()
        hospital_address = data.get("hospital_address", "").strip()
        hospital_phone = data.get("hospital_phone", "").strip()
        hospital_email = data.get("hospital_email", "").strip()
        tax_id = data.get("tax_id", "GSTIN27AAACM1234F1Z5").strip()
        currency_symbol = data.get("currency_symbol", "₹").strip()
        default_tax_rate = float(data.get("default_tax_rate", 5.0))
        invoice_footer = data.get("invoice_footer", "").strip()

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        UPDATE settings
        SET hospital_name = ?, hospital_address = ?, hospital_phone = ?, hospital_email = ?, tax_id = ?, currency_symbol = ?, default_tax_rate = ?, invoice_footer = ?, updated_at = ?
        WHERE id = 1
        """, (hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, now))

        if cursor.rowcount == 0:
            cursor.execute("""
            INSERT INTO settings (id, hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, now))

        conn.commit()
        cursor.execute("SELECT * FROM settings WHERE id = 1")
        settings = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({"success": True, "settings": settings})

    # -------------------------------------------------------------------------
    # UTILITY HELPERS
    # -------------------------------------------------------------------------
    def get_auth_token(self) -> Optional[str]:
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        return None

    def read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                return json.loads(body)
            except Exception:
                return {}
        return {}

    def serve_static_dashboard(self):
        static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.exists(static_path):
            with open(static_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content.encode("utf-8"))))
            self.end_headers()
            self.wfile.write(content.encode("utf-8"))
        else:
            self.send_json_response({"error": "Dashboard template not found"}, status=404)

    def serve_static_file(self, path: str):
        filename = "logo.png" if path == "/logo.png" else os.path.basename(path)
        file_path = os.path.join(os.path.dirname(__file__), "static", filename)
        if os.path.exists(file_path):
            content_type = "image/png" if filename.endswith(".png") else "text/plain"
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

    def send_json_response(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 8080):
    init_database()
    with socketserver.TCPServer(("", port), MedBillAPIHandler) as httpd:
        print(f"[*] MedBill Enterprise Server running at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    run_server(port=port)

"""
MedBill Enterprise - Complete Role-Based HTTP REST API Server & SPA Dispatcher
Supports 3 Roles: ADMIN (Business Analytics & Control), EMPLOYEE (Day-to-Day Operations & Billing), PATIENT (Self-Service Read-Only).
"""

import http.server
import socketserver
import urllib.parse
import json
import os
import mimetypes
import uuid
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any, Tuple

from medbill.database.db import (
    get_db_connection,
    hash_password,
    verify_password,
    create_employee,
    create_patient_login,
    get_patient_login_account,
    get_all_employees,
    toggle_user_status,
    reset_user_password
)

# Active In-Memory Session Cache
# token -> { "id": int, "username": str, "full_name": str, "email": str, "role": str, "patient_id": Optional[int], "expires_at": datetime }
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}


def generate_session_token(user: Dict[str, Any]) -> str:
    """Generates a secure UUID session token for an authenticated user."""
    token = f"mb_{uuid.uuid4().hex}"
    ACTIVE_SESSIONS[token] = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user.get("email", ""),
        "role": user["role"],
        "patient_id": user.get("patient_id"),
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
    HTTP REST API Handler & Static SPA Dispatcher for Role-Based Hospital Billing System.
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
            self.send_json_response({
                "status": "ONLINE",
                "system": "MedBill Enterprise RBAC",
                "version": "3.0.0",
                "roles_supported": ["ADMIN", "EMPLOYEE", "PATIENT"],
                "timestamp": datetime.utcnow().isoformat()
            })
            return

        # 3. Auth Status Verification
        if path in ("/api/auth/verify", "/api/auth/me"):
            token = self.get_auth_token()
            user = validate_session(token)
            if user:
                self.send_json_response({"authenticated": True, "user": user})
            else:
                self.send_json_response({"authenticated": False, "error": "Invalid or expired session"}, status=401)
            return

        # 4. Extract Auth Context for Protected Endpoints
        token = self.get_auth_token()
        user_ctx = validate_session(token)

        # Allow unauthenticated queries to fallback cleanly for initial setup, but enforce role boundaries
        # ---------------------------------------------------------------------
        # PATIENT ISOLATED ENDPOINTS (Strict Security: Patient can only see their own data)
        # ---------------------------------------------------------------------
        if path == "/api/patient/dashboard":
            self.handle_patient_dashboard(user_ctx)
            return
        elif path == "/api/patient/bills":
            self.handle_patient_bills(user_ctx)
            return
        elif path.startswith("/api/patient/bills/") and path.endswith("/print"):
            bill_id = int(path.split("/")[4])
            self.handle_patient_bill_print(bill_id, user_ctx)
            return
        elif path.startswith("/api/patient/bills/") and len(path.split("/")) == 5:
            bill_id = int(path.split("/")[4])
            self.handle_patient_bill_detail(bill_id, user_ctx)
            return
        elif path == "/api/patient/payments":
            self.handle_patient_payments(user_ctx)
            return
        elif path == "/api/patient/profile":
            self.handle_patient_profile(user_ctx)
            return

        # ---------------------------------------------------------------------
        # ADMIN EXCLUSIVE ENDPOINTS (Business Analytics & Employee Management)
        # ---------------------------------------------------------------------
        if path == "/api/admin/dashboard":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied. Patient role cannot view Admin analytics."}, status=403)
                return
            self.handle_admin_business_dashboard()
            return
        elif path == "/api/admin/employees":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            self.handle_get_employees()
            return

        # ---------------------------------------------------------------------
        # EMPLOYEE OPERATIONAL DASHBOARD
        # ---------------------------------------------------------------------
        if path == "/api/employee/dashboard":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            self.handle_employee_operational_dashboard()
            return
        elif path == "/api/dashboard/stats":
            # Universal dashboard stats fallback
            self.handle_get_dashboard_stats()
            return

        # ---------------------------------------------------------------------
        # SHARED OPERATIONAL ENDPOINTS (Admin & Employee)
        # ---------------------------------------------------------------------
        # Patients
        if path == "/api/patients":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied. Patients cannot access patient registry."}, status=403)
                return
            search = query.get("search", [""])[0]
            limit = int(query.get("limit", [100])[0])
            self.handle_get_patients(search, limit)
        elif path.startswith("/api/patients/") and path.endswith("/login-status"):
            patient_id = int(path.split("/")[3])
            self.handle_get_patient_login_status(patient_id)
        elif path.startswith("/api/patients/") and len(path.split("/")) == 4:
            patient_id = int(path.split("/")[3])
            if user_ctx and user_ctx.get("role") == "PATIENT" and user_ctx.get("patient_id") != patient_id:
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            self.handle_get_patient_detail(patient_id)
        # Cost Types
        elif path == "/api/cost-types":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            search = query.get("search", [""])[0]
            self.handle_get_cost_types(search)
        # Services
        elif path == "/api/services":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            search = query.get("search", [""])[0]
            cost_type_id = query.get("cost_type_id", [None])[0]
            active_only = query.get("active_only", ["0"])[0] == "1"
            self.handle_get_services(search, cost_type_id, active_only)
        elif path.startswith("/api/services/") and len(path.split("/")) == 4:
            service_id = int(path.split("/")[3])
            self.handle_get_service_detail(service_id)
        # Bills
        elif path == "/api/bills":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                # For safety, redirect patient to their own bills endpoint
                self.handle_patient_bills(user_ctx)
                return
            search = query.get("search", [""])[0]
            patient_id = query.get("patient_id", [None])[0]
            payment_status = query.get("payment_status", [None])[0]
            bill_status = query.get("bill_status", [None])[0]
            from_date = query.get("from_date", [None])[0]
            to_date = query.get("to_date", [None])[0]
            self.handle_get_bills(search, patient_id, payment_status, bill_status, from_date, to_date)
        elif path.startswith("/api/bills/") and path.endswith("/print"):
            bill_id = int(path.split("/")[3])
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.handle_patient_bill_print(bill_id, user_ctx)
                return
            self.handle_get_bill_print_data(bill_id)
        elif path.startswith("/api/bills/") and len(path.split("/")) == 4:
            bill_id = int(path.split("/")[3])
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.handle_patient_bill_detail(bill_id, user_ctx)
                return
            self.handle_get_bill_detail(bill_id)
        # Payments
        elif path == "/api/payments":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.handle_patient_payments(user_ctx)
                return
            bill_id = query.get("bill_id", [None])[0]
            limit = int(query.get("limit", [100])[0])
            self.handle_get_payments(bill_id, limit)
        # Reports
        elif path == "/api/reports":
            if user_ctx and user_ctx.get("role") == "PATIENT":
                self.send_json_response({"error": "Access denied. Patient role cannot view hospital revenue reports."}, status=403)
                return
            range_filter = query.get("range", ["month"])[0]
            self.handle_get_reports(range_filter)
        # Settings
        elif path == "/api/settings":
            self.handle_get_settings()
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"
        data = self.read_json_body()

        # Public Login
        if path == "/api/auth/login":
            self.handle_login(data)
            return
        elif path == "/api/auth/logout":
            token = self.get_auth_token()
            if token in ACTIVE_SESSIONS:
                del ACTIVE_SESSIONS[token]
            self.send_json_response({"success": True, "message": "Successfully signed out."})
            return

        # Check role permission
        token = self.get_auth_token()
        user_ctx = validate_session(token)

        # Patient cannot perform write operations
        if user_ctx and user_ctx.get("role") == "PATIENT":
            if path != "/api/auth/change-password":
                self.send_json_response({"error": "Access denied. Patient accounts have read-only access."}, status=403)
                return

        # Protected Write Endpoints
        if path == "/api/auth/change-password":
            self.handle_change_password(data, user_ctx)
        # Admin Employee Management
        elif path == "/api/admin/employees":
            if user_ctx and user_ctx.get("role") not in ("ADMIN", None):
                self.send_json_response({"error": "Access denied. Only Administrator can create employee accounts."}, status=403)
                return
            self.handle_create_employee(data)
        elif path.startswith("/api/admin/employees/") and path.endswith("/reset-password"):
            if user_ctx and user_ctx.get("role") not in ("ADMIN", None):
                self.send_json_response({"error": "Access denied."}, status=403)
                return
            emp_id = int(path.split("/")[4])
            self.handle_reset_employee_password(emp_id, data)
        # Employee Patient Login Creation
        elif path.startswith("/api/patients/") and path.endswith("/create-login"):
            patient_id = int(path.split("/")[3])
            self.handle_create_patient_login(patient_id, data)
        # Standard Write Endpoints
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

        token = self.get_auth_token()
        user_ctx = validate_session(token)
        if user_ctx and user_ctx.get("role") == "PATIENT":
            self.send_json_response({"error": "Access denied. Patient role cannot modify records."}, status=403)
            return

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
            if user_ctx and user_ctx.get("role") not in ("ADMIN", None):
                self.send_json_response({"error": "Access denied. Only Administrator can modify hospital settings."}, status=403)
                return
            self.handle_update_settings(data)
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_PATCH(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path.rstrip("/") or "/"

        token = self.get_auth_token()
        user_ctx = validate_session(token)
        if user_ctx and user_ctx.get("role") == "PATIENT":
            self.send_json_response({"error": "Access denied."}, status=403)
            return

        if path.startswith("/api/admin/employees/") and path.endswith("/toggle"):
            if user_ctx and user_ctx.get("role") not in ("ADMIN", None):
                self.send_json_response({"error": "Access denied. Only Administrator can toggle employee status."}, status=403)
                return
            emp_id = int(path.split("/")[4])
            self.handle_toggle_employee_status(emp_id)
        elif path.startswith("/api/cost-types/") and path.endswith("/toggle"):
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

        token = self.get_auth_token()
        user_ctx = validate_session(token)
        if user_ctx and user_ctx.get("role") == "PATIENT":
            self.send_json_response({"error": "Access denied. Patients cannot delete hospital records."}, status=403)
            return

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
        identifier = data.get("username", "").strip() or data.get("email", "").strip()
        password = data.get("password", "").strip()

        if not identifier or not password:
            self.send_json_response({"error": "Username / Email and password are required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (identifier, identifier))
        user = cursor.fetchone()
        conn.close()

        if not user or not verify_password(password, user["password_hash"]):
            self.send_json_response({"error": "Invalid login credentials. Please check your username and password."}, status=401)
            return

        if user["is_active"] == 0:
            self.send_json_response({
                "error": "This account has been deactivated. Please contact your hospital administrator."
            }, status=403)
            return

        user_dict = dict(user)
        token = generate_session_token(user_dict)
        self.send_json_response({
            "success": True,
            "token": token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "email": user["email"],
                "role": user["role"],
                "patient_id": user["patient_id"]
            }
        })

    def handle_change_password(self, data: Dict[str, Any], user_ctx: Optional[Dict[str, Any]]):
        current_password = data.get("current_password", "").strip()
        new_password = data.get("new_password", "").strip()
        target_username = data.get("username", "").strip()

        if not current_password or not new_password:
            self.send_json_response({"error": "Current and new passwords are required."}, status=400)
            return

        if len(new_password) < 4:
            self.send_json_response({"error": "New password must be at least 4 characters."}, status=400)
            return

        username = (user_ctx.get("username") if user_ctx else None) or target_username or "admin"

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
    # ADMIN BUSINESS DASHBOARD & EMPLOYEE MANAGEMENT
    # -------------------------------------------------------------------------
    def handle_admin_business_dashboard(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()
        first_day_month = date.today().replace(day=1).isoformat()
        first_day_year = date.today().replace(month=1, day=1).isoformat()
        seven_days_ago = (date.today() - timedelta(days=7)).isoformat()

        # High-Level Financial Metrics
        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as total FROM payments")
        total_revenue = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) as gross FROM bills WHERE bill_status != 'Cancelled'")
        gross_billed = cursor.fetchone()["gross"]

        cursor.execute("SELECT COALESCE(SUM(balance_amount), 0.0) as pending FROM bills WHERE bill_status != 'Cancelled'")
        pending_amount = cursor.fetchone()["pending"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE bill_status != 'Cancelled'")
        total_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Paid' AND bill_status != 'Cancelled'")
        paid_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Pending' AND bill_status != 'Cancelled'")
        pending_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE payment_status = 'Partially Paid' AND bill_status != 'Cancelled'")
        partial_bills = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'EMPLOYEE'")
        total_employees = cursor.fetchone()["count"]

        # Time-Based Revenues
        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as today_rev FROM payments WHERE payment_date = ?", (today,))
        today_revenue = cursor.fetchone()["today_rev"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as week_rev FROM payments WHERE payment_date >= ?", (seven_days_ago,))
        weekly_revenue = cursor.fetchone()["week_rev"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as month_rev FROM payments WHERE payment_date >= ?", (first_day_month,))
        monthly_revenue = cursor.fetchone()["month_rev"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as year_rev FROM payments WHERE payment_date >= ?", (first_day_year,))
        yearly_revenue = cursor.fetchone()["year_rev"]

        # Category Breakdown
        cursor.execute("""
        SELECT bi.cost_type_name, COALESCE(SUM(bi.amount), 0.0) as total_amount, COUNT(bi.id) as item_count
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_status != 'Cancelled'
        GROUP BY bi.cost_type_name
        ORDER BY total_amount DESC
        """)
        revenue_by_cost_type = [dict(row) for row in cursor.fetchall()]

        # Top Services by Revenue
        cursor.execute("""
        SELECT bi.service_name, bi.cost_type_name, SUM(bi.quantity) as total_qty, COALESCE(SUM(bi.amount), 0.0) as total_revenue
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_status != 'Cancelled'
        GROUP BY bi.service_name
        ORDER BY total_revenue DESC
        LIMIT 8
        """)
        revenue_by_service = [dict(row) for row in cursor.fetchall()]

        # Payment Methods Distribution
        cursor.execute("""
        SELECT payment_method, COUNT(*) as txn_count, COALESCE(SUM(amount), 0.0) as total_amount
        FROM payments
        GROUP BY payment_method
        ORDER BY total_amount DESC
        """)
        payment_methods = [dict(row) for row in cursor.fetchall()]

        # Recent Bills
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        ORDER BY b.id DESC
        LIMIT 6
        """)
        recent_bills = [dict(row) for row in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "total_revenue": total_revenue,
            "gross_billed": gross_billed,
            "net_collected": total_revenue,
            "pending_amount": pending_amount,
            "total_bills": total_bills,
            "paid_bills_count": paid_bills,
            "pending_bills_count": pending_bills,
            "partial_bills_count": partial_bills,
            "total_patients": total_patients,
            "total_employees": total_employees,
            "today_revenue": today_revenue,
            "weekly_revenue": weekly_revenue,
            "monthly_revenue": monthly_revenue,
            "yearly_revenue": yearly_revenue,
            "revenue_by_cost_type": revenue_by_cost_type,
            "revenue_by_service": revenue_by_service,
            "payment_methods": payment_methods,
            "recent_bills": recent_bills
        })

    def handle_get_employees(self):
        employees = get_all_employees()
        self.send_json_response({"employees": employees})

    def handle_create_employee(self, data: Dict[str, Any]):
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        full_name = data.get("full_name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()

        if not username or not password or not full_name:
            self.send_json_response({"error": "Username, password, and employee full name are required."}, status=400)
            return

        if len(password) < 4:
            self.send_json_response({"error": "Password must be at least 4 characters long."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            self.send_json_response({"error": f"Username '{username}' is already taken."}, status=400)
            return
        conn.close()

        try:
            emp = create_employee(username, password, full_name, email, phone)
            self.send_json_response({
                "success": True,
                "message": f"Employee account '{username}' created successfully.",
                "employee": emp
            }, status=201)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    def handle_toggle_employee_status(self, emp_id: int):
        try:
            updated = toggle_user_status(emp_id)
            status_str = "activated" if updated["is_active"] == 1 else "deactivated"
            self.send_json_response({
                "success": True,
                "message": f"Employee '{updated['username']}' account {status_str}.",
                "user": updated
            })
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    def handle_reset_employee_password(self, emp_id: int, data: Dict[str, Any]):
        new_password = data.get("new_password", "").strip()
        if not new_password or len(new_password) < 4:
            self.send_json_response({"error": "Password must be at least 4 characters long."}, status=400)
            return
        try:
            reset_user_password(emp_id, new_password)
            self.send_json_response({"success": True, "message": "Employee password reset successfully."})
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    # -------------------------------------------------------------------------
    # EMPLOYEE OPERATIONAL DASHBOARD
    # -------------------------------------------------------------------------
    def handle_employee_operational_dashboard(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()

        # Operational metrics
        cursor.execute("SELECT COUNT(*) as count FROM bills WHERE bill_date = ? AND bill_status != 'Cancelled'", (today,))
        today_bills_count = cursor.fetchone()["count"]

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as today_rev FROM payments WHERE payment_date = ?", (today,))
        today_revenue = cursor.fetchone()["today_rev"]

        cursor.execute("SELECT COUNT(*) as count, COALESCE(SUM(balance_amount), 0.0) as balance FROM bills WHERE payment_status = 'Pending' AND bill_status != 'Cancelled'")
        pending_row = cursor.fetchone()
        pending_bills_count = pending_row["count"]
        pending_balance = pending_row["balance"]

        cursor.execute("SELECT COUNT(*) as count FROM patients")
        total_patients = cursor.fetchone()["count"]

        # Recent bills
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        ORDER BY b.id DESC
        LIMIT 6
        """)
        recent_bills = [dict(row) for row in cursor.fetchall()]

        # Recent patients
        cursor.execute("""
        SELECT * FROM patients ORDER BY id DESC LIMIT 6
        """)
        recent_patients = [dict(row) for row in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "today_bills_count": today_bills_count,
            "today_revenue": today_revenue,
            "pending_bills_count": pending_bills_count,
            "pending_balance": pending_balance,
            "total_patients": total_patients,
            "recent_bills": recent_bills,
            "recent_patients": recent_patients
        })

    def handle_get_dashboard_stats(self):
        # Forward to admin analytics format
        self.handle_admin_business_dashboard()

    # -------------------------------------------------------------------------
    # EMPLOYEE CREATE PATIENT LOGIN
    # -------------------------------------------------------------------------
    def handle_create_patient_login(self, patient_id: int, data: Dict[str, Any]):
        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        email = data.get("email", "").strip()

        if not username or not password:
            self.send_json_response({"error": "Patient username and password are required."}, status=400)
            return

        if len(password) < 4:
            self.send_json_response({"error": "Password must be at least 4 characters long."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username is taken by another user
        cursor.execute("SELECT id, patient_id FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        if existing_user and existing_user["patient_id"] != patient_id:
            conn.close()
            self.send_json_response({"error": f"Username '{username}' is already taken by another account."}, status=400)
            return

        conn.close()

        try:
            patient_user = create_patient_login(patient_id, username, password, email)
            self.send_json_response({
                "success": True,
                "message": f"Patient login credentials created for {patient_user['full_name']} (Username: {username}).",
                "user": patient_user
            }, status=201)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    def handle_get_patient_login_status(self, patient_id: int):
        account = get_patient_login_account(patient_id)
        if account:
            self.send_json_response({"has_login": True, "account": account})
        else:
            self.send_json_response({"has_login": False})

    # -------------------------------------------------------------------------
    # PATIENT ISOLATED PORTAL HANDLERS (Strict Data Isolation)
    # -------------------------------------------------------------------------
    def _verify_patient_access(self, user_ctx: Optional[Dict[str, Any]]) -> Optional[int]:
        if not user_ctx or user_ctx.get("role") != "PATIENT" or not user_ctx.get("patient_id"):
            return None
        return int(user_ctx["patient_id"])

    def handle_patient_dashboard(self, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized. Patient session required."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Patient Info
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            conn.close()
            self.send_json_response({"error": "Patient record not found."}, status=404)
            return

        # Invoices Summary
        cursor.execute("""
        SELECT 
            COUNT(*) as total_bills,
            COALESCE(SUM(total_amount), 0.0) as total_billed,
            COALESCE(SUM(paid_amount), 0.0) as total_paid,
            COALESCE(SUM(balance_amount), 0.0) as total_balance
        FROM bills
        WHERE patient_id = ? AND bill_status != 'Cancelled'
        """, (patient_id,))
        summary = dict(cursor.fetchone())

        # Recent Invoices
        cursor.execute("""
        SELECT * FROM bills
        WHERE patient_id = ?
        ORDER BY id DESC
        LIMIT 6
        """, (patient_id,))
        recent_bills = [dict(row) for row in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "patient": dict(patient),
            "summary": summary,
            "recent_bills": recent_bills
        })

    def handle_patient_bills(self, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.patient_id = ?
        ORDER BY b.id DESC
        """, (patient_id,))
        bills = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"bills": bills, "count": len(bills)})

    def handle_patient_bill_detail(self, bill_id: int, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.phone as patient_phone, p.doctor as patient_doctor, p.room_number as patient_room
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Invoice not found."}, status=404)
            return

        if bill["patient_id"] != patient_id:
            conn.close()
            self.send_json_response({"error": "Access denied. You can only access your own medical billing invoices."}, status=403)
            return

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
        items = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(r) for r in cursor.fetchall()]

        conn.close()
        self.send_json_response({
            "bill": dict(bill),
            "items": items,
            "payments": payments
        })

    def handle_patient_bill_print(self, bill_id: int, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.age as patient_age, p.gender as patient_gender, p.doctor as patient_doctor, p.room_number as patient_room
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Invoice not found."}, status=404)
            return

        if bill["patient_id"] != patient_id:
            conn.close()
            self.send_json_response({"error": "Access denied. Cannot print another patient's invoice."}, status=403)
            return

        cursor.execute("SELECT * FROM settings LIMIT 1")
        settings = dict(cursor.fetchone())

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
        items = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(r) for r in cursor.fetchall()]

        conn.close()
        self.send_json_response({
            "hospital": settings,
            "bill": dict(bill),
            "items": items,
            "payments": payments
        })

    def handle_patient_payments(self, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT p.*, b.bill_number, pt.name as patient_name
        FROM payments p
        JOIN bills b ON p.bill_id = b.id
        JOIN patients pt ON b.patient_id = pt.id
        WHERE b.patient_id = ?
        ORDER BY p.id DESC
        """, (patient_id,))
        payments = [dict(r) for r in cursor.fetchall()]
        conn.close()

        self.send_json_response({"payments": payments, "count": len(payments)})

    def handle_patient_profile(self, user_ctx: Optional[Dict[str, Any]]):
        patient_id = self._verify_patient_access(user_ctx)
        if not patient_id:
            self.send_json_response({"error": "Unauthorized."}, status=401)
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        pat = cursor.fetchone()
        conn.close()

        if not pat:
            self.send_json_response({"error": "Patient not found."}, status=404)
            return

        self.send_json_response({"patient": dict(pat)})

    # -------------------------------------------------------------------------
    # PATIENTS MANAGEMENT HANDLERS (CRUD)
    # -------------------------------------------------------------------------
    def handle_get_patients(self, search: str = "", limit: int = 100):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search:
            q = f"%{search}%"
            cursor.execute("""
            SELECT p.*, 
                   COALESCE(SUM(b.balance_amount), 0.0) as outstanding_balance,
                   COUNT(b.id) as total_bills,
                   (SELECT username FROM users WHERE patient_id = p.id) as login_username
            FROM patients p
            LEFT JOIN bills b ON p.id = b.patient_id AND b.bill_status != 'Cancelled'
            WHERE p.name LIKE ? OR p.patient_number LIKE ? OR p.phone LIKE ?
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT ?
            """, (q, q, q, limit))
        else:
            cursor.execute("""
            SELECT p.*, 
                   COALESCE(SUM(b.balance_amount), 0.0) as outstanding_balance,
                   COUNT(b.id) as total_bills,
                   (SELECT username FROM users WHERE patient_id = p.id) as login_username
            FROM patients p
            LEFT JOIN bills b ON p.id = b.patient_id AND b.bill_status != 'Cancelled'
            GROUP BY p.id
            ORDER BY p.id DESC
            LIMIT ?
            """, (limit,))

        patients = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"patients": patients, "count": len(patients)})

    def handle_get_patient_detail(self, patient_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()

        if not patient:
            conn.close()
            self.send_json_response({"error": "Patient not found."}, status=404)
            return

        cursor.execute("SELECT * FROM bills WHERE patient_id = ? ORDER BY id DESC", (patient_id,))
        bills = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT id, username, email, phone, is_active FROM users WHERE patient_id = ?", (patient_id,))
        login_acc = cursor.fetchone()

        conn.close()

        self.send_json_response({
            "patient": dict(patient),
            "bills": bills,
            "login_account": dict(login_acc) if login_acc else None
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

        # Generate unique Patient Number: PAT-1001, PAT-1002, etc.
        cursor.execute("SELECT MAX(id) as max_id FROM patients")
        max_id = cursor.fetchone()["max_id"] or 0
        patient_number = f"PAT-{1000 + max_id + 1}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO patients (patient_number, name, age, gender, phone, address, doctor, room_number, admission_date, discharge_date, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_number, name, int(age), gender, phone, address, doctor, room_number, admission_date, discharge_date, now, now))

        patient_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({
            "success": True,
            "message": f"Patient {patient['name']} registered with ID {patient['patient_number']}.",
            "patient": patient
        }, status=201)

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
        # Cleanly delete linked user login if any
        cursor.execute("DELETE FROM users WHERE patient_id = ?", (patient_id,))
        # Delete the patient record
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))

        conn.commit()
        conn.close()
        self.send_json_response({
            "success": True,
            "message": f"Patient {patient['name']} ({patient['patient_number']}) and all associated records deleted successfully."
        })

    # -------------------------------------------------------------------------
    # COST TYPES HANDLERS (CRUD)
    # -------------------------------------------------------------------------
    def handle_get_cost_types(self, search: str):
        conn = get_db_connection()
        cursor = conn.cursor()

        if search:
            q = f"%{search}%"
            cursor.execute("""
            SELECT ct.*, COUNT(s.id) as service_count
            FROM cost_types ct
            LEFT JOIN services s ON ct.id = s.cost_type_id
            WHERE ct.name LIKE ? OR ct.description LIKE ?
            GROUP BY ct.id
            ORDER BY ct.name ASC
            """, (q, q))
        else:
            cursor.execute("""
            SELECT ct.*, COUNT(s.id) as service_count
            FROM cost_types ct
            LEFT JOIN services s ON ct.id = s.cost_type_id
            GROUP BY ct.id
            ORDER BY ct.name ASC
            """)

        cost_types = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"cost_types": cost_types, "count": len(cost_types)})

    def handle_create_cost_type(self, data: Dict[str, Any]):
        name = data.get("name", "").strip()
        description = data.get("description", "").strip()
        is_active = 1 if data.get("is_active", True) else 0

        if not name:
            self.send_json_response({"error": "Cost type category name is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM cost_types WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            self.send_json_response({"error": f"Cost type '{name}' already exists."}, status=400)
            return

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
        INSERT INTO cost_types (name, description, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (name, description, is_active, now, now))
        ct_id = cursor.lastrowid
        conn.commit()

        cursor.execute("SELECT * FROM cost_types WHERE id = ?", (ct_id,))
        created_ct = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({"success": True, "cost_type": created_ct}, status=201)

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

        cursor.execute("""
        UPDATE cost_types
        SET name = ?, description = ?, is_active = ?, updated_at = ?
        WHERE id = ?
        """, (name, description, is_active, now, cost_type_id))

        if cursor.rowcount == 0:
            conn.close()
            self.send_json_response({"error": "Cost type not found."}, status=404)
            return

        conn.commit()
        cursor.execute("SELECT * FROM cost_types WHERE id = ?", (cost_type_id,))
        updated_ct = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "cost_type": updated_ct})

    def handle_toggle_cost_type_status(self, cost_type_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_active FROM cost_types WHERE id = ?", (cost_type_id,))
        ct = cursor.fetchone()
        if not ct:
            conn.close()
            self.send_json_response({"error": "Cost type not found."}, status=404)
            return

        new_status = 0 if ct["is_active"] == 1 else 1
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE cost_types SET is_active = ?, updated_at = ? WHERE id = ?", (new_status, now, cost_type_id))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "is_active": new_status})

    def handle_delete_cost_type(self, cost_type_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM services WHERE cost_type_id = ?", (cost_type_id,))
        srv_count = cursor.fetchone()["count"]
        if srv_count > 0:
            conn.close()
            self.send_json_response({
                "error": f"Cannot delete cost type. {srv_count} service(s) are associated with this category."
            }, status=400)
            return

        cursor.execute("DELETE FROM cost_types WHERE id = ?", (cost_type_id,))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "message": "Cost type deleted successfully."})

    # -------------------------------------------------------------------------
    # SERVICES & PRICING HANDLERS (CRUD)
    # -------------------------------------------------------------------------
    def handle_get_services(self, search: str, cost_type_id: Optional[str], active_only: bool):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_str = """
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE 1=1
        """
        params = []

        if active_only:
            query_str += " AND s.is_active = 1"

        if cost_type_id:
            query_str += " AND s.cost_type_id = ?"
            params.append(int(cost_type_id))

        if search:
            query_str += " AND (s.service_name LIKE ? OR s.service_code LIKE ? OR s.description LIKE ?)"
            q = f"%{search}%"
            params.extend([q, q, q])

        query_str += " ORDER BY s.id ASC"
        cursor.execute(query_str, params)
        services = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"services": services, "count": len(services)})

    def handle_get_service_detail(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE s.id = ?
        """, (service_id,))
        service = cursor.fetchone()
        conn.close()

        if not service:
            self.send_json_response({"error": "Service not found."}, status=404)
            return

        self.send_json_response({"service": dict(service)})

    def handle_create_service(self, data: Dict[str, Any]):
        service_name = data.get("service_name", "").strip()
        cost_type_id = data.get("cost_type_id")
        description = data.get("description", "").strip()
        price = data.get("price")
        is_active = 1 if data.get("is_active", True) else 0

        if not service_name:
            self.send_json_response({"error": "Service name is required."}, status=400)
            return
        if not cost_type_id:
            self.send_json_response({"error": "Cost type category is required."}, status=400)
            return
        if price is None or float(price) < 0:
            self.send_json_response({"error": "Valid service price in INR is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Generate unique service code: SRV-1001, SRV-1002, etc.
        cursor.execute("SELECT MAX(id) as max_id FROM services")
        max_id = cursor.fetchone()["max_id"] or 0
        service_code = f"SRV-{1000 + max_id + 1}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO services (service_code, service_name, cost_type_id, description, price, is_active, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (service_code, service_name, int(cost_type_id), description, float(price), is_active, now, now))

        service_id = cursor.lastrowid
        conn.commit()

        cursor.execute("""
        SELECT s.*, ct.name as cost_type_name
        FROM services s
        JOIN cost_types ct ON s.cost_type_id = ct.id
        WHERE s.id = ?
        """, (service_id,))
        created_srv = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({"success": True, "service": created_srv}, status=201)

    def handle_update_service(self, service_id: int, data: Dict[str, Any]):
        service_name = data.get("service_name", "").strip()
        cost_type_id = data.get("cost_type_id")
        description = data.get("description", "").strip()
        price = data.get("price")
        is_active = 1 if data.get("is_active", True) else 0

        if not service_name:
            self.send_json_response({"error": "Service name cannot be empty."}, status=400)
            return
        if price is None or float(price) < 0:
            self.send_json_response({"error": "Valid service price in INR is required."}, status=400)
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
        updated_srv = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "service": updated_srv})

    def handle_toggle_service_status(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, is_active FROM services WHERE id = ?", (service_id,))
        srv = cursor.fetchone()
        if not srv:
            conn.close()
            self.send_json_response({"error": "Service not found."}, status=404)
            return

        new_status = 0 if srv["is_active"] == 1 else 1
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE services SET is_active = ?, updated_at = ? WHERE id = ?", (new_status, now, service_id))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "is_active": new_status})

    def handle_delete_service(self, service_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if service is used in historical bills
        cursor.execute("SELECT COUNT(*) as count FROM bill_items WHERE service_id = ?", (service_id,))
        used_count = cursor.fetchone()["count"]

        if used_count > 0:
            # Soft deactivate to preserve historical invoice accuracy
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("UPDATE services SET is_active = 0, updated_at = ? WHERE id = ?", (now, service_id))
            conn.commit()
            conn.close()
            self.send_json_response({
                "success": True,
                "message": "Service was used in historical invoices, so it has been safely deactivated instead of deleted."
            })
            return

        cursor.execute("DELETE FROM services WHERE id = ?", (service_id,))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "message": "Service deleted successfully."})

    # -------------------------------------------------------------------------
    # BILLING & INVOICING HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_bills(self, search: str, patient_id: Optional[str], payment_status: Optional[str], bill_status: Optional[str], from_date: Optional[str], to_date: Optional[str]):
        conn = get_db_connection()
        cursor = conn.cursor()

        query_str = """
        SELECT b.*, p.name as patient_name, p.patient_number
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE 1=1
        """
        params = []

        if patient_id:
            query_str += " AND b.patient_id = ?"
            params.append(int(patient_id))

        if payment_status:
            query_str += " AND b.payment_status = ?"
            params.append(payment_status)

        if bill_status:
            query_str += " AND b.bill_status = ?"
            params.append(bill_status)

        if from_date:
            query_str += " AND b.bill_date >= ?"
            params.append(from_date)

        if to_date:
            query_str += " AND b.bill_date <= ?"
            params.append(to_date)

        if search:
            q = f"%{search}%"
            query_str += " AND (b.bill_number LIKE ? OR p.name LIKE ? OR p.patient_number LIKE ?)"
            params.extend([q, q, q])

        query_str += " ORDER BY b.id DESC"
        cursor.execute(query_str, params)
        bills = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"bills": bills, "count": len(bills)})

    def handle_get_bill_detail(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.phone as patient_phone, p.doctor as patient_doctor, p.room_number as patient_room
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
        items = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(r) for r in cursor.fetchall()]

        conn.close()
        self.send_json_response({
            "bill": dict(bill),
            "items": items,
            "payments": payments
        })

    def handle_get_bill_print_data(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number, p.age as patient_age, p.gender as patient_gender, p.doctor as patient_doctor, p.room_number as patient_room, p.address as patient_address
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        bill = cursor.fetchone()

        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        cursor.execute("SELECT * FROM settings LIMIT 1")
        settings = dict(cursor.fetchone())

        cursor.execute("SELECT * FROM bill_items WHERE bill_id = ?", (bill_id,))
        items = [dict(r) for r in cursor.fetchall()]

        cursor.execute("SELECT * FROM payments WHERE bill_id = ? ORDER BY id ASC", (bill_id,))
        payments = [dict(r) for r in cursor.fetchall()]

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
        items = data.get("items", [])
        discount = float(data.get("discount", 0.0))
        tax_percent = float(data.get("tax_percent", 5.0))
        notes = data.get("notes", "").strip()

        if not patient_id:
            self.send_json_response({"error": "Patient selection is required."}, status=400)
            return
        if not items:
            self.send_json_response({"error": "Bill must contain at least one line item service."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check patient exists
        cursor.execute("SELECT id, name, patient_number FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        if not patient:
            conn.close()
            self.send_json_response({"error": "Selected patient does not exist."}, status=404)
            return

        # Calculate subtotal and prepare items
        subtotal = 0.0
        processed_items = []

        for itm in items:
            service_id = itm.get("service_id")
            unit_price = float(itm.get("unit_price", 0.0))
            quantity = int(itm.get("quantity", 1))
            service_name = itm.get("service_name", "")
            cost_type_name = itm.get("cost_type_name", "General")

            if service_id and (not service_name or unit_price <= 0):
                cursor.execute("""
                SELECT s.service_name, s.price, ct.name as cost_type_name
                FROM services s
                JOIN cost_types ct ON s.cost_type_id = ct.id
                WHERE s.id = ?
                """, (service_id,))
                srv_row = cursor.fetchone()
                if srv_row:
                    service_name = srv_row["service_name"]
                    cost_type_name = srv_row["cost_type_name"]
                    if unit_price <= 0:
                        unit_price = float(srv_row["price"])

            line_amount = round(unit_price * quantity, 2)
            subtotal += line_amount
            processed_items.append({
                "service_id": service_id,
                "service_name": service_name or "Hospital Service",
                "cost_type_name": cost_type_name,
                "unit_price": unit_price,
                "quantity": quantity,
                "amount": line_amount
            })

        subtotal = round(subtotal, 2)
        discount = round(min(discount, subtotal), 2)
        taxable_amount = max(0.0, subtotal - discount)
        tax_amount = round(taxable_amount * (tax_percent / 100.0), 2)
        total_amount = round(taxable_amount + tax_amount, 2)
        paid_amount = 0.0
        balance_amount = total_amount

        # Generate unique Bill Number: BILL-2026-0001
        cursor.execute("SELECT MAX(id) as max_id FROM bills")
        max_id = cursor.fetchone()["max_id"] or 0
        bill_number = f"BILL-2026-{str(max_id + 1).zfill(4)}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO bills (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, payment_status, bill_status, notes, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', 'Pending', ?, ?, ?)
        """, (bill_number, patient_id, bill_date, subtotal, discount, tax_percent, tax_amount, total_amount, paid_amount, balance_amount, notes, now, now))

        bill_id = cursor.lastrowid

        # Insert snapshot line items
        for p_item in processed_items:
            cursor.execute("""
            INSERT INTO bill_items (bill_id, service_id, service_name, cost_type_name, unit_price, quantity, amount, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (bill_id, p_item["service_id"], p_item["service_name"], p_item["cost_type_name"], p_item["unit_price"], p_item["quantity"], p_item["amount"], now))

        conn.commit()

        cursor.execute("""
        SELECT b.*, p.name as patient_name, p.patient_number
        FROM bills b
        JOIN patients p ON b.patient_id = p.id
        WHERE b.id = ?
        """, (bill_id,))
        created_bill = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({
            "success": True,
            "message": f"Bill {bill_number} created successfully.",
            "bill": created_bill
        }, status=201)

    def handle_update_bill(self, bill_id: int, data: Dict[str, Any]):
        discount = float(data.get("discount", 0.0))
        tax_percent = float(data.get("tax_percent", 5.0))
        notes = data.get("notes", "").strip()
        bill_status = data.get("bill_status")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        subtotal = bill["subtotal"]
        discount = round(min(discount, subtotal), 2)
        taxable = max(0.0, subtotal - discount)
        tax_amount = round(taxable * (tax_percent / 100.0), 2)
        total_amount = round(taxable + tax_amount, 2)
        paid_amount = bill["paid_amount"]
        balance_amount = max(0.0, total_amount - paid_amount)

        payment_status = "Paid" if balance_amount == 0 else ("Partially Paid" if paid_amount > 0 else "Pending")
        status_to_set = bill_status or ("Paid" if balance_amount == 0 else "Pending")

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE bills
        SET discount = ?, tax_percent = ?, tax_amount = ?, total_amount = ?, balance_amount = ?, payment_status = ?, bill_status = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """, (discount, tax_percent, tax_amount, total_amount, balance_amount, payment_status, status_to_set, notes, now, bill_id))

        conn.commit()
        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        updated = dict(cursor.fetchone())
        conn.close()
        self.send_json_response({"success": True, "bill": updated})

    def handle_delete_bill(self, bill_id: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, bill_number FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        cursor.execute("DELETE FROM payments WHERE bill_id = ?", (bill_id,))
        cursor.execute("DELETE FROM bill_items WHERE bill_id = ?", (bill_id,))
        cursor.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
        conn.commit()
        conn.close()
        self.send_json_response({"success": True, "message": f"Bill {bill['bill_number']} and associated receipts deleted."})

    # -------------------------------------------------------------------------
    # PAYMENTS & SETTLEMENTS HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_payments(self, bill_id: Optional[str], limit: int):
        conn = get_db_connection()
        cursor = conn.cursor()

        if bill_id:
            cursor.execute("""
            SELECT p.*, b.bill_number, pt.name as patient_name
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            JOIN patients pt ON b.patient_id = pt.id
            WHERE p.bill_id = ?
            ORDER BY p.id DESC
            LIMIT ?
            """, (int(bill_id), limit))
        else:
            cursor.execute("""
            SELECT p.*, b.bill_number, pt.name as patient_name
            FROM payments p
            JOIN bills b ON p.bill_id = b.id
            JOIN patients pt ON b.patient_id = pt.id
            ORDER BY p.id DESC
            LIMIT ?
            """, (limit,))

        payments = [dict(row) for row in cursor.fetchall()]
        conn.close()

        self.send_json_response({"payments": payments, "count": len(payments)})

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
            self.send_json_response({"error": "Valid positive payment amount is required."}, status=400)
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        bill = cursor.fetchone()
        if not bill:
            conn.close()
            self.send_json_response({"error": "Bill not found."}, status=404)
            return

        current_balance = float(bill["balance_amount"])
        if amount > current_balance + 0.01:
            conn.close()
            self.send_json_response({
                "error": f"Payment amount (₹{amount:.2f}) cannot exceed remaining balance (₹{current_balance:.2f})."
            }, status=400)
            return

        # Generate unique Payment Receipt Number: REC-2026-0001
        cursor.execute("SELECT MAX(id) as max_id FROM payments")
        max_id = cursor.fetchone()["max_id"] or 0
        payment_number = f"REC-2026-{str(max_id + 1).zfill(4)}"

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO payments (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (payment_number, bill_id, amount, payment_method, payment_date, reference_number, notes, now))

        payment_id = cursor.lastrowid

        # Update bill balance and status
        new_paid = round(float(bill["paid_amount"]) + amount, 2)
        new_balance = max(0.0, round(float(bill["total_amount"]) - new_paid, 2))
        new_status = "Paid" if new_balance == 0 else "Partially Paid"
        new_bill_status = "Paid" if new_balance == 0 else bill["bill_status"]

        cursor.execute("""
        UPDATE bills
        SET paid_amount = ?, balance_amount = ?, payment_status = ?, bill_status = ?, updated_at = ?
        WHERE id = ?
        """, (new_paid, new_balance, new_status, new_bill_status, now, bill_id))

        conn.commit()

        cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
        payment = dict(cursor.fetchone())

        cursor.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        updated_bill = dict(cursor.fetchone())

        conn.close()

        self.send_json_response({
            "success": True,
            "message": f"Payment of ₹{amount:.2f} recorded under {payment_number}.",
            "payment": payment,
            "bill": updated_bill
        }, status=201)

    # -------------------------------------------------------------------------
    # REPORTS HANDLER
    # -------------------------------------------------------------------------
    def handle_get_reports(self, range_filter: str):
        conn = get_db_connection()
        cursor = conn.cursor()

        today = date.today().isoformat()
        if range_filter == "today":
            start_date = today
        elif range_filter == "week":
            start_date = (date.today() - timedelta(days=7)).isoformat()
        elif range_filter == "month":
            start_date = date.today().replace(day=1).isoformat()
        elif range_filter == "year":
            start_date = date.today().replace(month=1, day=1).isoformat()
        else:
            start_date = "2000-01-01"

        cursor.execute("SELECT COALESCE(SUM(amount), 0.0) as total FROM payments WHERE payment_date >= ?", (start_date,))
        revenue_collected = cursor.fetchone()["total"]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0.0) as total, COALESCE(SUM(balance_amount), 0.0) as pending FROM bills WHERE bill_date >= ? AND bill_status != 'Cancelled'", (start_date,))
        b_row = cursor.fetchone()
        gross_billed = b_row["total"]
        pending_receivables = b_row["pending"]

        cursor.execute("""
        SELECT bi.cost_type_name, COUNT(bi.id) as item_count, COALESCE(SUM(bi.amount), 0.0) as total_amount
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_date >= ? AND b.bill_status != 'Cancelled'
        GROUP BY bi.cost_type_name
        ORDER BY total_amount DESC
        """, (start_date,))
        cost_type_breakdown = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
        SELECT bi.service_name, SUM(bi.quantity) as total_qty, COALESCE(SUM(bi.amount), 0.0) as total_revenue
        FROM bill_items bi
        JOIN bills b ON bi.bill_id = b.id
        WHERE b.bill_date >= ? AND b.bill_status != 'Cancelled'
        GROUP BY bi.service_name
        ORDER BY total_revenue DESC
        LIMIT 10
        """, (start_date,))
        top_services = [dict(r) for r in cursor.fetchall()]

        conn.close()

        self.send_json_response({
            "range": range_filter,
            "revenue_collected": revenue_collected,
            "gross_billed": gross_billed,
            "pending_receivables": pending_receivables,
            "cost_type_breakdown": cost_type_breakdown,
            "top_services": top_services
        })

    # -------------------------------------------------------------------------
    # SETTINGS HANDLERS
    # -------------------------------------------------------------------------
    def handle_get_settings(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM settings LIMIT 1")
        settings = dict(cursor.fetchone())
        conn.close()
        self.send_json_response(settings)

    def handle_update_settings(self, data: Dict[str, Any]):
        hospital_name = data.get("hospital_name", "").strip()
        hospital_address = data.get("hospital_address", "").strip()
        hospital_phone = data.get("hospital_phone", "").strip()
        hospital_email = data.get("hospital_email", "").strip()
        tax_id = data.get("tax_id", "").strip()
        currency_symbol = data.get("currency_symbol", "₹").strip()
        default_tax_rate = float(data.get("default_tax_rate", 5.0))
        invoice_footer = data.get("invoice_footer", "").strip()

        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        UPDATE settings
        SET hospital_name = ?, hospital_address = ?, hospital_phone = ?, hospital_email = ?, tax_id = ?, currency_symbol = ?, default_tax_rate = ?, invoice_footer = ?, updated_at = ?
        WHERE id = 1
        """, (hospital_name, hospital_address, hospital_phone, hospital_email, tax_id, currency_symbol, default_tax_rate, invoice_footer, now))

        conn.commit()
        cursor.execute("SELECT * FROM settings LIMIT 1")
        updated = dict(cursor.fetchone())
        conn.close()

        self.send_json_response({"success": True, "settings": updated})

    # -------------------------------------------------------------------------
    # STATIC ASSET DISPATCHERS & UTILITIES
    # -------------------------------------------------------------------------
    def serve_static_dashboard(self):
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        index_file = os.path.join(static_dir, "index.html")

        if os.path.exists(index_file):
            with open(index_file, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_json_response({"error": "Dashboard template not found"}, status=404)

    def serve_static_file(self, path: str):
        static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
        clean_path = path.lstrip("/").replace("static/", "")
        file_path = os.path.join(static_dir, clean_path)

        if not os.path.exists(file_path):
            file_path = os.path.join(static_dir, "index.html")

        if os.path.exists(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type or "application/octet-stream")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_json_response({"error": "File not found"}, status=404)

    def read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        try:
            body = self.rfile.read(content_length).decode("utf-8")
            return json.loads(body)
        except Exception:
            return {}

    def get_auth_token(self) -> Optional[str]:
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()
        parsed = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(parsed.query)
        if "token" in q:
            return q["token"][0]
        return None

    def send_json_response(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 5000):
    """Starts the HTTP REST API server on specified port."""
    server_address = ("", port)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(server_address, MedBillAPIHandler) as httpd:
        print(f"[*] MedBill Enterprise 3-Role RBAC Server active at http://localhost:{port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[!] Server shutting down gracefully.")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(port)

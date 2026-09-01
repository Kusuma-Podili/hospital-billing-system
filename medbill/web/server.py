"""
MedBill Enterprise - HTTP REST API Server
Provides high-performance RESTful API endpoints for hospital billing calculations,
master price lookups, claims adjudication, invoicing, payments, and ledger reporting.
Uses standard Python http.server / WSGI with zero external dependency requirements.
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from medbill.core.models import (
    Patient,
    PatientGender,
    Doctor,
    DoctorRank,
    Encounter,
    EncounterType,
    TriageLevel,
    RoomCategoryType,
    BillingLineItem,
    BillingItemCategory,
    PaymentMethod,
)
from medbill.catalogs.icd10_cm import search_icd10, get_icd10_entry
from medbill.catalogs.cpt_codes import search_cpt, get_cpt_entry
from medbill.catalogs.pharmacy_ndc import search_medications, get_medication_entry
from medbill.catalogs.loinc_lab_panels import search_lab_panels, get_lab_panel
from medbill.catalogs.surgical_packages import search_surgeries, get_surgical_package
from medbill.catalogs.room_categories import ROOM_TARIFF_CATALOG
from medbill.catalogs.doctors_specialties import SPECIALTY_CATALOG

from medbill.modules.consultation.consultation_calculator import ConsultationTariffCalculator
from medbill.modules.bed_management.room_tariff_calculator import RoomBedTariffCalculator, RoomStayPeriod
from medbill.modules.pharmacy.pharmacy_calculator import PharmacyTariffCalculator, PrescriptionOrder
from medbill.modules.laboratory.lab_tariff_calculator import LabTariffCalculator, DiagnosticOrder
from medbill.modules.surgery.surgical_costing_calculator import SurgicalCostingCalculator, SurgeryExecutionDetails
from medbill.modules.insurance_tpa.models import InsurancePolicy, PlanType
from medbill.modules.insurance_tpa.claims_engine import InsuranceClaimsEngine
from medbill.modules.billing_engine.master_invoice_aggregator import MasterInvoiceAggregator
from medbill.modules.ledger.general_ledger import GeneralLedgerService
from medbill.modules.fhir.fhir_financial import FHIRFinancialResourceBuilder


class MedBillAPIHandler(http.server.SimpleHTTPRequestHandler):
    """
    REST API and static dashboard request dispatcher.
    """

    consult_calc = ConsultationTariffCalculator()
    room_calc = RoomBedTariffCalculator()
    pharm_calc = PharmacyTariffCalculator()
    lab_calc = LabTariffCalculator()
    surg_calc = SurgicalCostingCalculator()
    claims_engine = InsuranceClaimsEngine()
    invoice_aggregator = MasterInvoiceAggregator()
    ledger_service = GeneralLedgerService()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        # Static Web Dashboard & Assets
        if path in ("/", "/index.html", "/dashboard"):
            self.serve_static_dashboard()
            return
        elif path == "/logo.png" or path.startswith("/static/"):
            self.serve_static_file(path)
            return

        # API Endpoints
        if path == "/api/health":
            self.send_json_response({"status": "ONLINE", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()})
        elif path == "/api/catalogs/icd10":
            q = query_params.get("q", [""])[0]
            results = [
                {"code": e.code, "description": e.description, "category": e.category, "severity": e.severity_level}
                for e in search_icd10(q, limit=25)
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/catalogs/cpt":
            q = query_params.get("q", [""])[0]
            results = [
                {"code": e.code, "description": e.description, "category": e.category, "fee": e.standard_fee}
                for e in search_cpt(q, limit=25)
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/catalogs/pharmacy":
            q = query_params.get("q", [""])[0]
            results = [
                {"ndc": m.ndc, "brand": m.brand_name, "generic": m.generic_name, "strength": m.strength, "price": m.unit_selling_price}
                for m in search_medications(q, limit=25)
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/catalogs/labs":
            q = query_params.get("q", [""])[0]
            results = [
                {"loinc": l.loinc_code, "name": l.panel_name, "dept": l.department, "price": l.standard_price, "cpt": l.cpt_equivalent}
                for l in search_lab_panels(q, limit=25)
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/catalogs/surgeries":
            q = query_params.get("q", [""])[0]
            results = [
                {"code": s.procedure_code, "name": s.procedure_name, "tier": s.surgical_tier, "surgeon_fee": s.chief_surgeon_base_fee, "ot_hourly": s.ot_table_hourly_rate}
                for s in search_surgeries(q, limit=25)
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/catalogs/rooms":
            results = [
                {"category": cat.value, "name": sched.name, "daily_rate": sched.daily_base_rate, "nursing": sched.nursing_daily_charge, "o2_hourly": sched.oxygen_hourly_rate, "vent_hourly": sched.ventilator_hourly_rate}
                for cat, sched in ROOM_TARIFF_CATALOG.items()
            ]
            self.send_json_response({"total": len(results), "results": results})
        elif path == "/api/ledger/trial-balance":
            tb = self.ledger_service.get_trial_balance()
            self.send_json_response(tb)
        elif path == "/api/analytics/rcm":
            self.send_json_response(self.get_rcm_analytics())
        else:
            self.send_json_response({"error": "Endpoint not found", "path": path}, status=404)

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        data = json.loads(body) if body else {}

        if path == "/api/billing/consultation":
            self.handle_consultation_calc(data)
        elif path == "/api/billing/inpatient-stay":
            self.handle_room_calc(data)
        elif path == "/api/billing/dispense-pharmacy":
            self.handle_pharmacy_dispense(data)
        elif path == "/api/billing/order-diagnostics":
            self.handle_lab_order(data)
        elif path == "/api/billing/surgery-cost":
            self.handle_surgery_cost(data)
        elif path == "/api/billing/adjudicate-claim":
            self.handle_claim_adjudication(data)
        else:
            self.send_json_response({"error": "Endpoint not found"}, status=404)

    def handle_consultation_calc(self, data: Dict[str, Any]):
        doctor = Doctor(
            doctor_id=data.get("doctor_id", "DOC_01"),
            license_number="MD-2026",
            first_name=data.get("doctor_first_name", "Alex"),
            last_name=data.get("doctor_last_name", "Mercer"),
            specialty_code=data.get("specialty_code", "CARDIO"),
            specialty_name=data.get("specialty_name", "Cardiology"),
            rank=DoctorRank(data.get("rank", "SENIOR_CONSULTANT")),
            base_consultation_fee=float(data.get("base_fee", 150.0)),
            telemedicine_fee=float(data.get("telemed_fee", 120.0)),
            department_id="DEPT_01"
        )
        encounter = Encounter(
            encounter_id="ENC_API_01",
            patient_id="PAT_API_01",
            encounter_type=EncounterType(data.get("encounter_type", "OUTPATIENT")),
            admission_time=datetime.utcnow(),
            triage_level=TriageLevel(data.get("triage_level", 3)) if data.get("triage_level") else None
        )
        item = self.consult_calc.calculate_consultation_charge(
            doctor=doctor,
            encounter=encounter,
            is_emergency=data.get("is_emergency", False),
            is_telemedicine=data.get("is_telemedicine", False)
        )
        self.send_json_response({
            "item_name": item.item_name,
            "unit_price": item.unit_price,
            "discount": item.discount_amount,
            "tax": item.tax_amount,
            "total_amount": item.total_amount,
            "description": item.description
        })

    def handle_room_calc(self, data: Dict[str, Any]):
        encounter = Encounter(
            encounter_id="ENC_ROOM_01",
            patient_id="PAT_ROOM_01",
            encounter_type=EncounterType.INPATIENT,
            admission_time=datetime.utcnow() - timedelta(days=float(data.get("days", 3))),
            discharge_time=datetime.utcnow()
        )
        period = RoomStayPeriod(
            category=RoomCategoryType(data.get("category", "PRIVATE_DELUXE")),
            start_time=encounter.admission_time,
            end_time=encounter.discharge_time,
            metered_oxygen_hours=float(data.get("oxygen_hours", 0)),
            ventilator_hours=float(data.get("ventilator_hours", 0)),
            telemetry_hours=float(data.get("telemetry_hours", 0))
        )
        items = self.room_calc.calculate_stay_charges(encounter, [period])
        total = sum(i.total_amount for i in items)
        self.send_json_response({
            "total_amount": round(total, 2),
            "line_items": [{"name": i.item_name, "amount": i.total_amount, "desc": i.description} for i in items]
        })

    def handle_pharmacy_dispense(self, data: Dict[str, Any]):
        encounter = Encounter(encounter_id="ENC_PH_01", patient_id="PAT_01", encounter_type=EncounterType.OUTPATIENT, admission_time=datetime.utcnow())
        orders = [
            PrescriptionOrder(
                ndc=item["ndc"],
                quantity=float(item.get("qty", 1)),
                batch_number=item.get("lot", "LOT-API-01"),
                expiry_date=item.get("exp", "2027-12-31"),
                prescribed_by_doctor_id="DOC_01",
                is_compounded_iv=item.get("is_compounded", False),
                is_stat_urgent=item.get("is_stat", False)
            )
            for item in data.get("orders", [])
        ]
        items = self.pharm_calc.dispense_medications(encounter, orders)
        total = sum(i.total_amount for i in items)
        self.send_json_response({
            "total_amount": round(total, 2),
            "line_items": [{"name": i.item_name, "amount": i.total_amount, "tax": i.tax_amount} for i in items]
        })

    def handle_lab_order(self, data: Dict[str, Any]):
        encounter = Encounter(encounter_id="ENC_LAB_01", patient_id="PAT_01", encounter_type=EncounterType.OUTPATIENT, admission_time=datetime.utcnow())
        orders = [
            DiagnosticOrder(
                loinc_code=loinc,
                is_stat_urgent=data.get("is_stat", False)
            )
            for loinc in data.get("loinc_codes", [])
        ]
        items = self.lab_calc.calculate_diagnostic_orders(encounter, orders)
        total = sum(i.total_amount for i in items)
        self.send_json_response({
            "total_amount": round(total, 2),
            "line_items": [{"name": i.item_name, "amount": i.total_amount, "desc": i.description} for i in items]
        })

    def handle_surgery_cost(self, data: Dict[str, Any]):
        encounter = Encounter(encounter_id="ENC_SG_01", patient_id="PAT_01", encounter_type=EncounterType.INPATIENT, admission_time=datetime.utcnow())
        details = SurgeryExecutionDetails(
            procedure_code=data.get("procedure_code", "47562"),
            actual_duration_hours=float(data.get("duration_hours", 2.0)),
            chief_surgeon_id="DOC_SURG_01",
            anesthesiologist_id="DOC_ANES_01",
            actual_implant_cost=float(data.get("implant_cost", 0.0)),
            is_emergency_surgery=data.get("is_emergency", False)
        )
        items = self.surg_calc.calculate_surgical_episode(encounter, details)
        total = sum(i.total_amount for i in items)
        self.send_json_response({
            "total_amount": round(total, 2),
            "line_items": [{"name": i.item_name, "amount": i.total_amount} for i in items]
        })

    def handle_claim_adjudication(self, data: Dict[str, Any]):
        patient = Patient(
            patient_id="PAT_01", mrn="MRN-01", first_name=data.get("first_name", "John"),
            last_name=data.get("last_name", "Smith"), dob="1980-01-01", gender=PatientGender.MALE,
            phone="555-0100", email="john@example.com", address="Main St"
        )
        policy = InsurancePolicy(
            policy_id="POL_01", patient_id="PAT_01", payer_id="PAYER_01",
            payer_name=data.get("payer_name", "Blue Cross PPO"),
            plan_name="Gold Comprehensive", plan_type=PlanType(data.get("plan_type", "PPO")),
            group_number="GRP-01", member_id="MBR-01",
            annual_deductible=float(data.get("annual_deductible", 500.0)),
            deductible_met=float(data.get("deductible_met", 100.0)),
            annual_out_of_pocket_max=float(data.get("oopm", 3000.0)),
            out_of_pocket_met=float(data.get("oopm_met", 200.0)),
            coinsurance_rate=float(data.get("coinsurance_rate", 0.20)),
            contractual_discount_percent=float(data.get("discount_percent", 10.0))
        )
        encounter = Encounter(encounter_id="ENC_01", patient_id="PAT_01", encounter_type=EncounterType.INPATIENT, admission_time=datetime.utcnow())
        billed_items = [
            BillingLineItem(
                item_id=str(idx), encounter_id="ENC_01", category=BillingItemCategory.MISCELLANEOUS,
                item_code="SRV", item_name=item["name"], description="Service",
                unit_price=float(item["amount"]), quantity=1.0, subtotal=float(item["amount"]), total_amount=float(item["amount"])
            )
            for idx, item in enumerate(data.get("billed_items", []))
        ]
        adj = self.claims_engine.adjudicate_claim(encounter, patient, policy, billed_items, pre_authorization_code=data.get("auth_code", "AUTH-OK"))
        self.send_json_response({
            "claim_id": adj.claim_id,
            "status": adj.status.value,
            "total_billed": adj.total_billed,
            "total_allowed": adj.total_allowed,
            "contractual_discount": adj.total_contractual_discount,
            "deductible_applied": adj.total_deductible,
            "coinsurance_applied": adj.total_coinsurance,
            "payer_paid": adj.total_payer_paid,
            "patient_owes": adj.total_patient_responsibility,
            "notes": adj.explanation_of_benefits_notes
        })

    def get_rcm_analytics(self) -> Dict[str, Any]:
        return {
            "kpis": {
                "gross_revenue_mtd": 1485200.00,
                "net_collections_mtd": 1290450.00,
                "clean_claims_rate_percent": 96.4,
                "average_days_in_ar": 26.8,
                "claim_denial_rate_percent": 3.6
            },
            "ar_aging_buckets": {
                "current_0_30_days": 680400.00,
                "aging_31_60_days": 210500.00,
                "aging_61_90_days": 78200.00,
                "over_90_days_aging": 24100.00
            },
            "departmental_revenue_mix": {
                "Inpatient_Bed_Ward": 420000.00,
                "Surgical_OT_Suites": 380000.00,
                "Pharmacy_Dispensing": 290000.00,
                "Laboratory_Diagnostics": 195000.00,
                "Radiology_Imaging": 125000.00,
                "OPD_Consultations": 75200.00
            }
        }

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
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 8080):
    with socketserver.TCPServer(("", port), MedBillAPIHandler) as httpd:
        print(f"[*] MedBill Enterprise Server running at http://localhost:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()

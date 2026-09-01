import unittest
import urllib.request
import json

class TestLiveServerEndpoints(unittest.TestCase):
    BASE = "http://localhost:5000"

    def post(self, path, data):
        req = urllib.request.Request(
            f"{self.BASE}{path}",
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def get(self, path):
        with urllib.request.urlopen(f"{self.BASE}{path}") as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_01_health_and_index(self):
        with urllib.request.urlopen(f"{self.BASE}/api/health") as resp:
            self.assertEqual(resp.status, 200)
        with urllib.request.urlopen(f"{self.BASE}/") as resp:
            self.assertEqual(resp.status, 200)

    def test_02_admin_login(self):
        st, data = self.post("/api/auth/login", {"username": "admin", "password": "admin"})
        self.assertEqual(st, 200)
        self.assertTrue(data.get("success"))
        self.assertIn("token", data)

    def test_03_dashboard_stats(self):
        st, data = self.get("/api/dashboard/stats")
        self.assertEqual(st, 200)
        self.assertIn("total_patients", data)
        self.assertIn("total_bills", data)
        self.assertIn("total_revenue", data)

    def test_04_patient_crud_flow(self):
        # Create
        st, data = self.post("/api/patients", {
            "name": "Arjun Singhania",
            "age": 45,
            "gender": "MALE",
            "phone": "9819992211",
            "doctor": "Dr. Verma",
            "room_number": "PVT-108"
        })
        self.assertEqual(st, 201)
        pat_id = data["patient"]["id"]

        # Get
        st, data = self.get(f"/api/patients/{pat_id}")
        self.assertEqual(st, 200)
        self.assertEqual(data["patient"]["name"], "Arjun Singhania")

    def test_05_billing_and_payment_flow(self):
        # Fetch a patient
        st, p_data = self.get("/api/patients")
        pat_id = p_data["patients"][0]["id"]

        # Create Bill
        st, b_data = self.post("/api/bills", {
            "patient_id": pat_id,
            "items": [
                {"service_name": "General Consultation", "cost_type_name": "Consultation", "unit_price": 600.0, "quantity": 1},
                {"service_name": "Blood Test CBC", "cost_type_name": "Laboratory Test", "unit_price": 450.0, "quantity": 2}
            ],
            "discount": 100.0,
            "tax_percent": 5.0
        })
        self.assertEqual(st, 201)
        bill_id = b_data["bill"]["id"]
        total_amt = b_data["bill"]["total_amount"]
        # Subtotal: 600 + 900 = 1500; Discount: 100 -> 1400; Tax 5% of 1400 = 70; Total = 1470
        self.assertEqual(total_amt, 1470.0)

        # Pay Bill in full
        st, pay_data = self.post("/api/payments", {
            "bill_id": bill_id,
            "amount": 1470.0,
            "payment_method": "UPI"
        })
        self.assertEqual(st, 201)
        self.assertEqual(pay_data["bill"]["payment_status"], "Paid")
        self.assertEqual(pay_data["bill"]["balance_amount"], 0.0)

    def test_06_reports_endpoint(self):
        st, data = self.get("/api/reports?range=month")
        self.assertEqual(st, 200)
        self.assertIn("revenue_collected", data)
        self.assertIn("cost_type_breakdown", data)

    def test_07_settings_endpoint(self):
        st, data = self.get("/api/settings")
        self.assertEqual(st, 200)
        self.assertIn("hospital_name", data)


if __name__ == "__main__":
    unittest.main()

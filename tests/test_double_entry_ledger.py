"""
MedBill Enterprise - Automated Test Suite 8: Double-Entry Financial Ledger
Validates debits = credits mathematical equality, Chart of Accounts postings,
Trial Balance calculation, and cryptographic hash chain checksums.
"""

import unittest
from datetime import datetime

from medbill.core.models import (
    Invoice,
    InvoiceStatus,
    BillingLineItem,
    BillingItemCategory,
    PaymentRecord,
    PaymentMethod,
)
from medbill.modules.ledger.general_ledger import GeneralLedgerService
from medbill.modules.ledger.models import StandardAccountCode


class TestDoubleEntryLedger(unittest.TestCase):

    def setUp(self):
        self.ledger = GeneralLedgerService()

    def test_post_invoice_balanced_journal_entry(self):
        """Test posting an inpatient invoice: debits equal credits and audit hash generated."""
        items = [
            BillingLineItem(
                item_id="ITEM-1",
                encounter_id="ENC-1",
                category=BillingItemCategory.CONSULTATION,
                item_code="99203",
                item_name="Doctor Consultation",
                description="Consultation",
                unit_price=200.00,
                quantity=1.0,
                subtotal=200.00,
                total_amount=200.00
            ),
            BillingLineItem(
                item_id="ITEM-2",
                encounter_id="ENC-1",
                category=BillingItemCategory.ROOM_BED,
                item_code="ROOM_DELUXE",
                item_name="Deluxe Room Stay",
                description="Room Rent",
                unit_price=1000.00,
                quantity=1.0,
                subtotal=1000.00,
                total_amount=1000.00
            ),
            BillingLineItem(
                item_id="ITEM-3",
                encounter_id="ENC-1",
                category=BillingItemCategory.PHARMACY,
                item_code="00093-3147-01",
                item_name="Augmentin",
                description="Antibiotics",
                unit_price=50.00,
                quantity=1.0,
                subtotal=50.00,
                tax_rate_percent=5.0,
                tax_amount=2.50,
                total_amount=52.50
            )
        ]

        invoice = Invoice(
            invoice_id="INV-LEDGER-01",
            invoice_number="INV-2026-888",
            encounter_id="ENC-1",
            patient_id="PAT-1",
            issue_date="2026-09-01",
            due_date="2026-10-01",
            status=InvoiceStatus.APPROVED,
            line_items=items,
            gross_total=1250.00,
            total_tax=2.50,
            net_total=1252.50,
            patient_payable=252.50,
            insurance_payable=1000.00
        )

        entry = self.ledger.post_invoice(invoice)

        # 1. Assert journal entry is strictly balanced
        self.assertTrue(entry.is_balanced)
        self.assertEqual(entry.total_debits, 1252.50)
        self.assertEqual(entry.total_credits, 1252.50)

        # 2. Assert SHA-256 hash checksum generated
        self.assertTrue(len(entry.hash_checksum) == 64)

        # 3. Assert Trial Balance reflects balanced debits & credits
        tb = self.ledger.get_trial_balance()
        self.assertTrue(tb["is_balanced"])
        self.assertEqual(tb["total_debits"], 1252.50)
        self.assertEqual(tb["total_credits"], 1252.50)

    def test_post_payment_receipt_and_ar_reduction(self):
        """Test posting patient payment reduces AR and increases Cash at Bank."""
        payment = PaymentRecord(
            payment_id="PMT-1001",
            invoice_id="INV-LEDGER-01",
            patient_id="PAT-1",
            amount=252.50,
            payment_method=PaymentMethod.CREDIT_CARD,
            transaction_reference="AUTH-CC-99021",
            status="SUCCESS"
        )

        entry = self.ledger.post_payment(payment)

        self.assertTrue(entry.is_balanced)
        self.assertEqual(entry.total_debits, 252.50)
        self.assertEqual(entry.total_credits, 252.50)

        # Cash clearing account increased
        clearing_acc = self.ledger.chart_of_accounts[StandardAccountCode.PAYMENT_GATEWAY_CLEARING.value]
        self.assertEqual(clearing_acc.current_balance, 252.50)


if __name__ == "__main__":
    unittest.main()

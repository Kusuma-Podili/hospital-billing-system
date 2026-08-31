"""
MedBill Enterprise - Master Invoice Aggregator & Split-Billing Engine
Aggregates Consultation, Room, Pharmacy, Diagnostics, and Surgery line items into a unified Master Invoice.
Executes dynamic multi-payer split-billing across Insurance, Corporate Sponsors, Subsidies, and Patient Out-of-Pocket.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import uuid

from medbill.core.models import (
    Patient,
    Encounter,
    BillingLineItem,
    Invoice,
    InvoiceStatus,
    PaymentRecord,
    PaymentMethod,
)
from medbill.modules.insurance_tpa.models import AdjudicationSummary


class MasterInvoiceAggregator:
    """
    Consolidates clinical encounter billing line items, applies multi-payer splits,
    vouchers, hardship discounts, and produces finalized fiscal invoices.
    """

    def create_master_invoice(
        self,
        encounter: Encounter,
        patient: Patient,
        line_items: List[BillingLineItem],
        adjudication: Optional[AdjudicationSummary] = None,
        sponsor_share_percent: float = 0.0,
        hardship_discount_percent: float = 0.0,
        notes: str = ""
    ) -> Invoice:
        """
        Creates and aggregates an enterprise master invoice with multi-payer split billing.
        """
        inv_id = str(uuid.uuid4())
        inv_number = f"INV-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"
        issue_date = datetime.utcnow().strftime("%Y-%m-%d")
        due_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")

        invoice = Invoice(
            invoice_id=inv_id,
            invoice_number=inv_number,
            encounter_id=encounter.encounter_id,
            patient_id=patient.patient_id,
            issue_date=issue_date,
            due_date=due_date,
            status=InvoiceStatus.APPROVED,
            line_items=line_items,
            notes=notes
        )
        invoice.recalculate()

        # Split Payer Allocations
        if adjudication:
            # Payer Share from insurance adjudication
            invoice.insurance_payable = adjudication.total_payer_paid
            # Contractual PPO discount is recorded in total_discount
            remaining_balance = adjudication.total_patient_responsibility
        else:
            remaining_balance = invoice.net_total

        # Corporate Sponsor Share (if employer / sponsor subsidy)
        if sponsor_share_percent > 0:
            sponsor_portion = round(remaining_balance * (sponsor_share_percent / 100.0), 2)
            invoice.sponsor_payable = sponsor_portion
            remaining_balance -= sponsor_portion

        # Hardship / Indigent Charity Care Waiver
        if hardship_discount_percent > 0:
            hardship_waiver = round(remaining_balance * (hardship_discount_percent / 100.0), 2)
            invoice.total_discount += hardship_waiver
            remaining_balance -= hardship_waiver

        invoice.patient_payable = round(max(0.0, remaining_balance), 2)
        invoice.balance_due = round(invoice.patient_payable + invoice.insurance_payable + invoice.sponsor_payable, 2)
        return invoice

    def record_payment(
        self,
        invoice: Invoice,
        amount: float,
        payment_method: PaymentMethod,
        transaction_reference: Optional[str] = None
    ) -> PaymentRecord:
        """
        Applies a payment to the invoice and returns a verifiable payment record.
        """
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")

        tx_ref = transaction_reference or f"TXN-{uuid.uuid4().hex[:8].upper()}"
        payment = PaymentRecord(
            payment_id=str(uuid.uuid4()),
            invoice_id=invoice.invoice_id,
            patient_id=invoice.patient_id,
            amount=amount,
            payment_method=payment_method,
            transaction_reference=tx_ref,
            status="SUCCESS"
        )

        invoice.paid_amount = round(invoice.paid_amount + amount, 2)
        invoice.recalculate()
        return payment

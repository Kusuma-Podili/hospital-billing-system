"""
MedBill Enterprise - Double-Entry General Ledger Service
Maintains the Chart of Accounts, executes balanced journal postings for Invoices,
Claims Adjudication, Payments, and Refunds, and generates Trial Balance & Financial Reports.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from medbill.core.models import (
    Invoice,
    PaymentRecord,
    PaymentMethod,
    BillingItemCategory,
)
from medbill.core.exceptions import LedgerImbalanceError
from medbill.modules.ledger.models import (
    Account,
    AccountType,
    StandardAccountCode,
    JournalPostingLine,
    JournalEntry,
)


class GeneralLedgerService:
    """
    Enterprise Double-Entry Bookkeeping Ledger.
    """

    def __init__(self):
        self.chart_of_accounts: Dict[str, Account] = self._initialize_chart_of_accounts()
        self.journal_entries: List[JournalEntry] = []
        self.last_entry_hash = "0000000000000000"

    def _initialize_chart_of_accounts(self) -> Dict[str, Account]:
        return {
            StandardAccountCode.CASH_OPERATING_BANK.value: Account(
                StandardAccountCode.CASH_OPERATING_BANK.value, "Cash at Bank (Operating)", AccountType.ASSET, "Hospital primary operating bank account"
            ),
            StandardAccountCode.PAYMENT_GATEWAY_CLEARING.value: Account(
                StandardAccountCode.PAYMENT_GATEWAY_CLEARING.value, "Payment Gateway Clearing", AccountType.ASSET, "Credit Card / UPI in-transit clearing"
            ),
            StandardAccountCode.ACCOUNTS_RECEIVABLE_PATIENT.value: Account(
                StandardAccountCode.ACCOUNTS_RECEIVABLE_PATIENT.value, "Accounts Receivable - Patient", AccountType.ASSET, "Unpaid patient out-of-pocket bills"
            ),
            StandardAccountCode.ACCOUNTS_RECEIVABLE_INSURANCE.value: Account(
                StandardAccountCode.ACCOUNTS_RECEIVABLE_INSURANCE.value, "Accounts Receivable - Insurance", AccountType.ASSET, "Pending insurance / TPA claims"
            ),
            StandardAccountCode.ACCOUNTS_RECEIVABLE_CORPORATE.value: Account(
                StandardAccountCode.ACCOUNTS_RECEIVABLE_CORPORATE.value, "Accounts Receivable - Corporate", AccountType.ASSET, "Corporate employer sponsored receivables"
            ),
            StandardAccountCode.PATIENT_ADVANCE_DEPOSITS.value: Account(
                StandardAccountCode.PATIENT_ADVANCE_DEPOSITS.value, "Patient Advance Deposits", AccountType.LIABILITY, "Pre-admission patient deposit escrow"
            ),
            StandardAccountCode.DISPENSING_TAX_PAYABLE.value: Account(
                StandardAccountCode.DISPENSING_TAX_PAYABLE.value, "Pharmacy Tax Payable", AccountType.LIABILITY, "Sales tax / GST collected on medications"
            ),
            StandardAccountCode.REV_OPD_CONSULTATION.value: Account(
                StandardAccountCode.REV_OPD_CONSULTATION.value, "Revenue - OPD Consultation", AccountType.REVENUE, "Doctor outpatient visit charges"
            ),
            StandardAccountCode.REV_INPATIENT_ROOM_BED.value: Account(
                StandardAccountCode.REV_INPATIENT_ROOM_BED.value, "Revenue - Inpatient Room & Ward", AccountType.REVENUE, "Ward and Deluxe bed rent"
            ),
            StandardAccountCode.REV_ICU_CRITICAL_CARE.value: Account(
                StandardAccountCode.REV_ICU_CRITICAL_CARE.value, "Revenue - ICU Critical Care", AccountType.REVENUE, "ICU bed, monitoring and life support"
            ),
            StandardAccountCode.REV_PHARMACY_MEDICATIONS.value: Account(
                StandardAccountCode.REV_PHARMACY_MEDICATIONS.value, "Revenue - Pharmacy Sales", AccountType.REVENUE, "Prescription medications and IV infusions"
            ),
            StandardAccountCode.REV_LABORATORY_DIAGNOSTICS.value: Account(
                StandardAccountCode.REV_LABORATORY_DIAGNOSTICS.value, "Revenue - Laboratory Diagnostics", AccountType.REVENUE, "Hematology, biochemistry and microbiology tests"
            ),
            StandardAccountCode.REV_RADIOLOGY_IMAGING.value: Account(
                StandardAccountCode.REV_RADIOLOGY_IMAGING.value, "Revenue - Radiology & Imaging", AccountType.REVENUE, "X-Ray, CT, MRI and Ultrasound scans"
            ),
            StandardAccountCode.REV_SURGICAL_PROCEDURES.value: Account(
                StandardAccountCode.REV_SURGICAL_PROCEDURES.value, "Revenue - Surgical Procedures", AccountType.REVENUE, "Operating theater and surgical packages"
            ),
            StandardAccountCode.REV_ANESTHESIA_SERVICES.value: Account(
                StandardAccountCode.REV_ANESTHESIA_SERVICES.value, "Revenue - Anesthesia Services", AccountType.REVENUE, "Anesthesiologist intraoperative care"
            ),
            StandardAccountCode.REV_MEDICAL_GAS_EQUIPMENT.value: Account(
                StandardAccountCode.REV_MEDICAL_GAS_EQUIPMENT.value, "Revenue - Medical Gas & Equipment", AccountType.REVENUE, "Oxygen delivery and mechanical ventilators"
            ),
            StandardAccountCode.CONTRACTUAL_ALLOWANCE_DISCOUNT.value: Account(
                StandardAccountCode.CONTRACTUAL_ALLOWANCE_DISCOUNT.value, "Contractual Allowance & Discount", AccountType.EXPENSE, "Negotiated PPO in-network discounts"
            ),
            StandardAccountCode.CHARITY_CARE_HARDSHIP_WAIVER.value: Account(
                StandardAccountCode.CHARITY_CARE_HARDSHIP_WAIVER.value, "Charity Care & Hardship Waiver", AccountType.EXPENSE, "Indigent patient financial assistance"
            )
        }

    def post_invoice(self, invoice: Invoice) -> JournalEntry:
        """
        Creates and posts a double-entry journal entry for a generated hospital invoice.
        Debits: Accounts Receivable (Patient, Insurance, Sponsor) + Contractual Discounts
        Credits: Departmental Revenue Accounts + Tax Payable
        """
        entry_id = str(uuid.uuid4())
        entry_number = f"JE-INV-{len(self.journal_entries) + 1:06d}"
        postings: List[JournalPostingLine] = []

        # 1. Debits: Receivables
        if invoice.patient_payable > 0:
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=StandardAccountCode.ACCOUNTS_RECEIVABLE_PATIENT.value,
                account_name="Accounts Receivable - Patient",
                debit_amount=invoice.patient_payable,
                credit_amount=0.0,
                memo=f"Patient portion for {invoice.invoice_number}"
            ))

        if invoice.insurance_payable > 0:
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=StandardAccountCode.ACCOUNTS_RECEIVABLE_INSURANCE.value,
                account_name="Accounts Receivable - Insurance",
                debit_amount=invoice.insurance_payable,
                credit_amount=0.0,
                memo=f"Insurance claim for {invoice.invoice_number}"
            ))

        if invoice.sponsor_payable > 0:
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=StandardAccountCode.ACCOUNTS_RECEIVABLE_CORPORATE.value,
                account_name="Accounts Receivable - Corporate",
                debit_amount=invoice.sponsor_payable,
                credit_amount=0.0,
                memo=f"Corporate sponsor portion for {invoice.invoice_number}"
            ))

        if invoice.total_discount > 0:
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=StandardAccountCode.CONTRACTUAL_ALLOWANCE_DISCOUNT.value,
                account_name="Contractual Allowance & Discount",
                debit_amount=invoice.total_discount,
                credit_amount=0.0,
                memo=f"Institutional discounts for {invoice.invoice_number}"
            ))

        # 2. Credits: Revenue by Department
        revenue_map: Dict[str, float] = {}
        for item in invoice.line_items:
            rev_code = self._map_category_to_revenue_account(item.category, item.item_code)
            revenue_map[rev_code] = revenue_map.get(rev_code, 0.0) + item.subtotal

        for rev_code, amt in revenue_map.items():
            acc = self.chart_of_accounts.get(rev_code)
            acc_name = acc.account_name if acc else "Departmental Revenue"
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=rev_code,
                account_name=acc_name,
                debit_amount=0.0,
                credit_amount=round(amt, 2),
                memo=f"Departmental revenue for {invoice.invoice_number}"
            ))

        # Tax Payable Credit
        if invoice.total_tax > 0:
            postings.append(JournalPostingLine(
                posting_id=str(uuid.uuid4()),
                account_code=StandardAccountCode.DISPENSING_TAX_PAYABLE.value,
                account_name="Pharmacy Tax Payable",
                debit_amount=0.0,
                credit_amount=invoice.total_tax,
                memo=f"Tax collected on {invoice.invoice_number}"
            ))

        # Create Journal Entry
        entry = JournalEntry(
            entry_id=entry_id,
            entry_number=entry_number,
            timestamp=datetime.utcnow().isoformat(),
            reference_id=invoice.invoice_id,
            description=f"Revenue Recognition for Invoice #{invoice.invoice_number}",
            posting_lines=postings,
            previous_hash=self.last_entry_hash
        )
        entry.validate_and_compute_hash()

        if not entry.is_balanced:
            raise LedgerImbalanceError(entry.total_debits, entry.total_credits)

        self._apply_postings_to_balances(entry)
        self.journal_entries.append(entry)
        self.last_entry_hash = entry.hash_checksum
        return entry

    def post_payment(self, payment: PaymentRecord) -> JournalEntry:
        """
        Posts a journal entry for patient or insurer payment.
        Debit: Cash / Payment Gateway
        Credit: Accounts Receivable
        """
        entry_id = str(uuid.uuid4())
        entry_number = f"JE-PMT-{len(self.journal_entries) + 1:06d}"
        postings: List[JournalPostingLine] = []

        cash_account = (
            StandardAccountCode.CASH_OPERATING_BANK.value
            if payment.payment_method in (PaymentMethod.CASH, PaymentMethod.BANK_TRANSFER)
            else StandardAccountCode.PAYMENT_GATEWAY_CLEARING.value
        )

        # Debit: Cash / Clearing
        postings.append(JournalPostingLine(
            posting_id=str(uuid.uuid4()),
            account_code=cash_account,
            account_name="Cash at Bank / Clearing",
            debit_amount=payment.amount,
            credit_amount=0.0,
            memo=f"Payment received via {payment.payment_method.value} (Ref: {payment.transaction_reference})"
        ))

        # Credit: Accounts Receivable
        ar_code = (
            StandardAccountCode.ACCOUNTS_RECEIVABLE_INSURANCE.value
            if payment.payment_method == PaymentMethod.INSURANCE_DIRECT
            else StandardAccountCode.ACCOUNTS_RECEIVABLE_PATIENT.value
        )
        postings.append(JournalPostingLine(
            posting_id=str(uuid.uuid4()),
            account_code=ar_code,
            account_name="Accounts Receivable",
            debit_amount=0.0,
            credit_amount=payment.amount,
            memo=f"Receivable settlement for Invoice #{payment.invoice_id}"
        ))

        entry = JournalEntry(
            entry_id=entry_id,
            entry_number=entry_number,
            timestamp=datetime.utcnow().isoformat(),
            reference_id=payment.payment_id,
            description=f"Payment Receipt #{payment.transaction_reference} for Invoice #{payment.invoice_id}",
            posting_lines=postings,
            previous_hash=self.last_entry_hash
        )
        entry.validate_and_compute_hash()

        if not entry.is_balanced:
            raise LedgerImbalanceError(entry.total_debits, entry.total_credits)

        self._apply_postings_to_balances(entry)
        self.journal_entries.append(entry)
        self.last_entry_hash = entry.hash_checksum
        return entry

    def _map_category_to_revenue_account(self, category: BillingItemCategory, item_code: str) -> str:
        if category == BillingItemCategory.CONSULTATION:
            return StandardAccountCode.REV_OPD_CONSULTATION.value
        elif category == BillingItemCategory.ROOM_BED:
            return StandardAccountCode.REV_ICU_CRITICAL_CARE.value if "ICU" in item_code or "CCU" in item_code else StandardAccountCode.REV_INPATIENT_ROOM_BED.value
        elif category == BillingItemCategory.PHARMACY:
            return StandardAccountCode.REV_PHARMACY_MEDICATIONS.value
        elif category == BillingItemCategory.LABORATORY:
            return StandardAccountCode.REV_LABORATORY_DIAGNOSTICS.value
        elif category == BillingItemCategory.RADIOLOGY:
            return StandardAccountCode.REV_RADIOLOGY_IMAGING.value
        elif category == BillingItemCategory.SURGERY:
            return StandardAccountCode.REV_SURGICAL_PROCEDURES.value
        elif category == BillingItemCategory.ANESTHESIA:
            return StandardAccountCode.REV_ANESTHESIA_SERVICES.value
        elif category in (BillingItemCategory.MEDICAL_GAS, BillingItemCategory.EQUIPMENT):
            return StandardAccountCode.REV_MEDICAL_GAS_EQUIPMENT.value
        return StandardAccountCode.REV_OPD_CONSULTATION.value

    def _apply_postings_to_balances(self, entry: JournalEntry) -> None:
        for p in entry.posting_lines:
            acc = self.chart_of_accounts.get(p.account_code)
            if not acc:
                continue
            if acc.account_type in (AccountType.ASSET, AccountType.EXPENSE):
                acc.current_balance += (p.debit_amount - p.credit_amount)
            else:
                acc.current_balance += (p.credit_amount - p.debit_amount)

    def get_trial_balance(self) -> Dict[str, Any]:
        """Generates real-time Trial Balance report."""
        total_debits = 0.0
        total_credits = 0.0
        accounts_summary = []

        for acc in self.chart_of_accounts.values():
            if acc.account_type in (AccountType.ASSET, AccountType.EXPENSE):
                debit_bal = acc.current_balance if acc.current_balance > 0 else 0.0
                credit_bal = abs(acc.current_balance) if acc.current_balance < 0 else 0.0
            else:
                credit_bal = acc.current_balance if acc.current_balance > 0 else 0.0
                debit_bal = abs(acc.current_balance) if acc.current_balance < 0 else 0.0

            total_debits += debit_bal
            total_credits += credit_bal

            accounts_summary.append({
                "code": acc.account_code,
                "name": acc.account_name,
                "type": acc.account_type.value,
                "debit": round(debit_bal, 2),
                "credit": round(credit_bal, 2)
            })

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "accounts": accounts_summary,
            "total_debits": round(total_debits, 2),
            "total_credits": round(total_credits, 2),
            "is_balanced": abs(total_debits - total_credits) < 0.01
        }

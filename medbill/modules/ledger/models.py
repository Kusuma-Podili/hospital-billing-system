"""
MedBill Enterprise - Double-Entry Financial Ledger Data Models
Defines Chart of Accounts, Journal Entries, Ledger Postings, and Audit Trail.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any
import hashlib
import uuid


class AccountType(str, Enum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class StandardAccountCode(str, Enum):
    # Assets (1000 - 1999)
    CASH_OPERATING_BANK = "1010"
    PAYMENT_GATEWAY_CLEARING = "1020"
    ACCOUNTS_RECEIVABLE_PATIENT = "1110"
    ACCOUNTS_RECEIVABLE_INSURANCE = "1120"
    ACCOUNTS_RECEIVABLE_CORPORATE = "1130"
    PHARMACY_INVENTORY = "1210"
    SURGICAL_IMPLANT_INVENTORY = "1220"

    # Liabilities (2000 - 2999)
    PATIENT_ADVANCE_DEPOSITS = "2010"
    DISPENSING_TAX_PAYABLE = "2110"
    UNEARNED_REVENUE = "2210"

    # Equity (3000 - 3999)
    RETAINED_EARNINGS = "3010"

    # Revenue (4000 - 4999)
    REV_OPD_CONSULTATION = "4010"
    REV_EMERGENCY_TRIAGE = "4020"
    REV_INPATIENT_ROOM_BED = "4030"
    REV_ICU_CRITICAL_CARE = "4040"
    REV_PHARMACY_MEDICATIONS = "4050"
    REV_LABORATORY_DIAGNOSTICS = "4060"
    REV_RADIOLOGY_IMAGING = "4070"
    REV_SURGICAL_PROCEDURES = "4080"
    REV_ANESTHESIA_SERVICES = "4090"
    REV_MEDICAL_GAS_EQUIPMENT = "4100"

    # Expenses & Contra-Revenue (5000 - 5999)
    CONTRACTUAL_ALLOWANCE_DISCOUNT = "5010"
    CHARITY_CARE_HARDSHIP_WAIVER = "5020"
    BAD_DEBT_EXPENSE = "5030"


@dataclass
class Account:
    account_code: str
    account_name: str
    account_type: AccountType
    description: str
    current_balance: float = 0.0


@dataclass
class JournalPostingLine:
    posting_id: str
    account_code: str
    account_name: str
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    memo: str = ""


@dataclass
class JournalEntry:
    entry_id: str
    entry_number: str
    timestamp: str
    reference_id: str  # Invoice ID, Payment ID, Refund ID
    description: str
    posting_lines: List[JournalPostingLine] = field(default_factory=list)
    total_debits: float = 0.0
    total_credits: float = 0.0
    is_balanced: bool = False
    previous_hash: str = "0000000000000000"
    hash_checksum: str = ""

    def validate_and_compute_hash(self) -> None:
        self.total_debits = round(sum(p.debit_amount for p in self.posting_lines), 2)
        self.total_credits = round(sum(p.credit_amount for p in self.posting_lines), 2)
        
        # Check debit = credit balance
        diff = abs(self.total_debits - self.total_credits)
        self.is_balanced = diff < 0.001

        # Cryptographic Hash Chain Checksum for Immutable Financial Audit Trail
        payload = f"{self.entry_id}|{self.entry_number}|{self.timestamp}|{self.reference_id}|{self.total_debits}|{self.total_credits}|{self.previous_hash}"
        self.hash_checksum = hashlib.sha256(payload.encode('utf-8')).hexdigest()

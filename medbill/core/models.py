"""
MedBill Enterprise Core - Domain Models & Data Structures
Enterprise Hospital Billing & Revenue Cycle Management System
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union
import uuid
import json


class EncounterType(str, Enum):
    OUTPATIENT = "OUTPATIENT"
    INPATIENT = "INPATIENT"
    EMERGENCY = "EMERGENCY"
    DAYCARE = "DAYCARE"
    TELEMEDICINE = "TELEMEDICINE"


class PatientGender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class DoctorRank(str, Enum):
    JUNIOR_RESIDENT = "JUNIOR_RESIDENT"
    ATTENDING_PHYSICIAN = "ATTENDING_PHYSICIAN"
    SENIOR_CONSULTANT = "SENIOR_CONSULTANT"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    EMERITUS_PROFESSOR = "EMERITUS_PROFESSOR"


class TriageLevel(int, Enum):
    LEVEL_1_RESUSCITATION = 1
    LEVEL_2_EMERGENT = 2
    LEVEL_3_URGENT = 3
    LEVEL_4_SEMI_URGENT = 4
    LEVEL_5_NON_URGENT = 5


class RoomCategoryType(str, Enum):
    GENERAL_WARD_MALE = "GENERAL_WARD_MALE"
    GENERAL_WARD_FEMALE = "GENERAL_WARD_FEMALE"
    SEMI_PRIVATE_ROOM = "SEMI_PRIVATE_ROOM"
    PRIVATE_DELUXE = "PRIVATE_DELUXE"
    SUPER_DELUXE_SUITE = "SUPER_DELUXE_SUITE"
    PRESIDENTIAL_SUITE = "PRESIDENTIAL_SUITE"
    INTENSIVE_CARE_UNIT_ICU = "INTENSIVE_CARE_UNIT_ICU"
    CORONARY_CARE_UNIT_CCU = "CORONARY_CARE_UNIT_CCU"
    NEONATAL_ICU_NICU = "NEONATAL_ICU_NICU"
    PEDIATRIC_ICU_PICU = "PEDIATRIC_ICU_PICU"
    HIGH_DEPENDENCY_UNIT_HDU = "HIGH_DEPENDENCY_UNIT_HDU"
    ISOLATION_WARD = "ISOLATION_WARD"
    DAYCARE_BED = "DAYCARE_BED"
    EMERGENCY_OBSERVATION = "EMERGENCY_OBSERVATION"


class BillingItemCategory(str, Enum):
    CONSULTATION = "CONSULTATION"
    ROOM_BED = "ROOM_BED"
    PHARMACY = "PHARMACY"
    LABORATORY = "LABORATORY"
    RADIOLOGY = "RADIOLOGY"
    SURGERY = "SURGERY"
    ANESTHESIA = "ANESTHESIA"
    EQUIPMENT = "EQUIPMENT"
    MEDICAL_GAS = "MEDICAL_GAS"
    NURSING = "NURSING"
    PHYSIOTHERAPY = "PHYSIOTHERAPY"
    AMBULANCE = "AMBULANCE"
    MISCELLANEOUS = "MISCELLANEOUS"


class InvoiceStatus(str, Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"


class PaymentMethod(str, Enum):
    CASH = "CASH"
    CREDIT_CARD = "CREDIT_CARD"
    DEBIT_CARD = "DEBIT_CARD"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    INSURANCE_DIRECT = "INSURANCE_DIRECT"
    CORPORATE_SPONSOR = "CORPORATE_SPONSOR"
    GOVERNMENT_SCHEME = "GOVERNMENT_SCHEME"
    ESCROW_DEPOSIT = "ESCROW_DEPOSIT"


class ClaimStatus(str, Enum):
    QUEUED = "QUEUED"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    PRE_AUTHORIZED = "PRE_AUTHORIZED"
    ADJUDICATED_PAID = "ADJUDICATED_PAID"
    ADJUDICATED_PARTIAL = "ADJUDICATED_PARTIAL"
    DENIED = "DENIED"
    APPEALED = "APPEALED"


@dataclass
class Patient:
    patient_id: str
    mrn: str  # Medical Record Number
    first_name: str
    last_name: str
    dob: str
    gender: PatientGender
    phone: str
    email: str
    address: str
    blood_group: str = "O+"
    emergency_contact: str = ""
    insurance_policy_id: Optional[str] = None
    national_health_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


@dataclass
class Doctor:
    doctor_id: str
    license_number: str
    first_name: str
    last_name: str
    specialty_code: str
    specialty_name: str
    rank: DoctorRank
    base_consultation_fee: float
    telemedicine_fee: float
    department_id: str
    phone: str = ""
    email: str = ""
    is_active: bool = True

    @property
    def full_name(self) -> str:
        return f"Dr. {self.first_name} {self.last_name}"


@dataclass
class Encounter:
    encounter_id: str
    patient_id: str
    encounter_type: EncounterType
    admission_time: datetime
    discharge_time: Optional[datetime] = None
    attending_doctor_id: Optional[str] = None
    department_id: Optional[str] = None
    primary_icd10_code: Optional[str] = None
    secondary_icd10_codes: List[str] = field(default_factory=list)
    triage_level: Optional[TriageLevel] = None
    bed_id: Optional[str] = None
    room_category: Optional[RoomCategoryType] = None
    is_discharged: bool = False
    notes: str = ""


@dataclass
class BillingLineItem:
    item_id: str
    encounter_id: str
    category: BillingItemCategory
    item_code: str  # CPT, NDC, LOINC, or internal code
    item_name: str
    description: str
    unit_price: float
    quantity: float
    subtotal: float
    discount_amount: float = 0.0
    tax_rate_percent: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    performed_by_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_totals(self) -> None:
        self.subtotal = round(self.unit_price * self.quantity, 2)
        base_after_discount = max(0.0, self.subtotal - self.discount_amount)
        self.tax_amount = round(base_after_discount * (self.tax_rate_percent / 100.0), 2)
        self.total_amount = round(base_after_discount + self.tax_amount, 2)


@dataclass
class Invoice:
    invoice_id: str
    invoice_number: str
    encounter_id: str
    patient_id: str
    issue_date: str
    due_date: str
    status: InvoiceStatus
    line_items: List[BillingLineItem] = field(default_factory=list)
    gross_total: float = 0.0
    total_discount: float = 0.0
    total_tax: float = 0.0
    net_total: float = 0.0
    patient_payable: float = 0.0
    insurance_payable: float = 0.0
    sponsor_payable: float = 0.0
    paid_amount: float = 0.0
    balance_due: float = 0.0
    currency: str = "USD"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    notes: str = ""

    def recalculate(self) -> None:
        self.gross_total = round(sum(item.subtotal for item in self.line_items), 2)
        self.total_discount = round(sum(item.discount_amount for item in self.line_items), 2)
        self.total_tax = round(sum(item.tax_amount for item in self.line_items), 2)
        self.net_total = round(sum(item.total_amount for item in self.line_items), 2)
        
        # If split is not specified, default to patient payable
        if self.insurance_payable == 0.0 and self.sponsor_payable == 0.0:
            self.patient_payable = self.net_total
        
        self.balance_due = round(max(0.0, self.net_total - self.paid_amount), 2)
        if self.paid_amount >= self.net_total and self.net_total > 0:
            self.status = InvoiceStatus.PAID
        elif self.paid_amount > 0:
            self.status = InvoiceStatus.PARTIALLY_PAID


@dataclass
class PaymentRecord:
    payment_id: str
    invoice_id: str
    patient_id: str
    amount: float
    payment_method: PaymentMethod
    transaction_reference: str
    payment_date: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    status: str = "SUCCESS"
    notes: str = ""


@dataclass
class AuditLog:
    log_id: str
    timestamp: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    details: Dict[str, Any]
    hash_checksum: str = ""

"""
MedBill Enterprise - Health Insurance, TPA & Claims Data Models
Defines insurance policies, benefit tiers, deductible accumulators, co-payments,
co-insurance, out-of-pocket maximums, and claim adjudication records.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any
import uuid


class PlanType(str, Enum):
    HMO = "HMO"  # Health Maintenance Organization
    PPO = "PPO"  # Preferred Provider Organization
    EPO = "EPO"  # Exclusive Provider Organization
    POS = "POS"  # Point of Service
    HDHP = "HDHP"  # High Deductible Health Plan
    MEDICARE = "MEDICARE"
    MEDICAID = "MEDICAID"
    GOVERNMENT_SCHEME = "GOVERNMENT_SCHEME"  # e.g., Ayushman Bharat PM-JAY
    COMMERCIAL_TPA = "COMMERCIAL_TPA"


class ClaimType(str, Enum):
    PROFESSIONAL = "PROFESSIONAL"  # CMS-1500 (HCFA-1500)
    INSTITUTIONAL = "INSTITUTIONAL"  # UB-04 (CMS-1450)
    PHARMACY = "PHARMACY"  # NCPDP D.0


class AdjudicationStatus(str, Enum):
    APPROVED = "APPROVED"
    PARTIALLY_APPROVED = "PARTIALLY_APPROVED"
    DENIED = "DENIED"
    REQUIRES_PRE_AUTH = "REQUIRES_PRE_AUTH"
    PENDING_ADDITIONAL_INFO = "PENDING_ADDITIONAL_INFO"


@dataclass
class InsurancePolicy:
    policy_id: str
    patient_id: str
    payer_id: str
    payer_name: str
    plan_name: str
    plan_type: PlanType
    group_number: str
    member_id: str
    annual_deductible: float
    deductible_met: float  # Amount satisfied so far this policy year
    annual_out_of_pocket_max: float  # OOPM
    out_of_pocket_met: float  # OOP satisfied so far
    coinsurance_rate: float  # e.g. 0.20 for 80/20 plan (patient pays 20% after deductible)
    copay_general_opd: float = 20.00
    copay_specialist_opd: float = 40.00
    copay_emergency: float = 150.00
    copay_inpatient_daily: float = 0.00
    pre_auth_required_for_inpatient: bool = True
    pre_auth_required_for_surgery: bool = True
    pre_auth_threshold_amount: float = 1000.00
    contractual_discount_percent: float = 15.00  # PPO in-network negotiated discount
    is_active: bool = True
    effective_date: str = "2026-01-01"
    expiration_date: str = "2026-12-31"

    def is_valid_for_date(self, check_date: str) -> bool:
        """Check if policy is active on a given date (YYYY-MM-DD)."""
        if not self.is_active:
            return False
        return self.effective_date <= check_date <= self.expiration_date


@dataclass
class ClaimLineAdjudication:
    line_item_id: str
    item_code: str
    item_name: str
    billed_amount: float
    contractual_allowed_amount: float
    contractual_discount: float
    deductible_applied: float
    copay_applied: float
    coinsurance_applied: float
    payer_covered_amount: float
    patient_responsibility: float
    status: AdjudicationStatus
    carc_reason_code: Optional[str] = None  # Claim Adjustment Reason Code (e.g. CO-45, PR-1)
    carc_reason_description: Optional[str] = None


@dataclass
class AdjudicationSummary:
    claim_id: str
    encounter_id: str
    policy_id: str
    payer_name: str
    total_billed: float
    total_contractual_discount: float
    total_allowed: float
    total_deductible: float
    total_copay: float
    total_coinsurance: float
    total_payer_paid: float
    total_patient_responsibility: float
    status: AdjudicationStatus
    line_adjudications: List[ClaimLineAdjudication] = field(default_factory=list)
    adjudication_timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    explanation_of_benefits_notes: str = ""

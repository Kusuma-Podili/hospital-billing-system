"""
MedBill Enterprise - Custom Domain Exceptions
"""


class MedBillError(Exception):
    """Base exception for all MedBill errors."""
    def __init__(self, message: str, error_code: str = "GENERIC_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class TariffNotFoundError(MedBillError):
    def __init__(self, item_code: str, category: str):
        super().__init__(
            f"Tariff rate not found for code '{item_code}' in category '{category}'",
            error_code="TARIFF_NOT_FOUND",
            details={"item_code": item_code, "category": category}
        )


class PatientNotFoundError(MedBillError):
    def __init__(self, patient_id: str):
        super().__init__(
            f"Patient with ID '{patient_id}' not found",
            error_code="PATIENT_NOT_FOUND",
            details={"patient_id": patient_id}
        )


class DoctorNotFoundError(MedBillError):
    def __init__(self, doctor_id: str):
        super().__init__(
            f"Doctor with ID '{doctor_id}' not found",
            error_code="DOCTOR_NOT_FOUND",
            details={"doctor_id": doctor_id}
        )


class EncounterClosedError(MedBillError):
    def __init__(self, encounter_id: str):
        super().__init__(
            f"Cannot modify billing for closed/discharged encounter '{encounter_id}'",
            error_code="ENCOUNTER_CLOSED",
            details={"encounter_id": encounter_id}
        )


class InsurancePolicyExpiredError(MedBillError):
    def __init__(self, policy_id: str, expiry_date: str):
        super().__init__(
            f"Insurance policy '{policy_id}' expired on {expiry_date}",
            error_code="INSURANCE_EXPIRED",
            details={"policy_id": policy_id, "expiry_date": expiry_date}
        )


class InvalidPaymentAmountError(MedBillError):
    def __init__(self, amount: float, balance_due: float):
        super().__init__(
            f"Payment amount ${amount:.2f} exceeds outstanding balance ${balance_due:.2f}",
            error_code="INVALID_PAYMENT_AMOUNT",
            details={"amount": amount, "balance_due": balance_due}
        )


class LedgerImbalanceError(MedBillError):
    def __init__(self, total_debits: float, total_credits: float):
        super().__init__(
            f"Double-entry ledger imbalance! Debits (${total_debits:.2f}) != Credits (${total_credits:.2f})",
            error_code="LEDGER_IMBALANCE",
            details={"total_debits": total_debits, "total_credits": total_credits}
        )

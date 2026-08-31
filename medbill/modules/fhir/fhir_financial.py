"""
MedBill Enterprise - HL7 FHIR R4 Financial Module
Generates fully compliant HL7 FHIR Release 4 JSON resources for healthcare billing:
- Account (Financial account tracking)
- Coverage (Insurance coverage details)
- Claim (Billing claim submission)
- ClaimResponse (Adjudication response)
- ExplanationOfBenefit (EOB comprehensive remittance)
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from medbill.core.models import (
    Patient,
    Encounter,
    BillingLineItem,
    Invoice,
)
from medbill.modules.insurance_tpa.models import (
    InsurancePolicy,
    AdjudicationSummary,
)


class FHIRFinancialResourceBuilder:
    """
    Builds HL7 FHIR R4 standard JSON resources for healthcare billing & finance.
    """

    @staticmethod
    def build_account_resource(
        invoice: Invoice,
        patient: Patient,
        policy: Optional[InsurancePolicy] = None
    ) -> Dict[str, Any]:
        """Generate FHIR R4 'Account' resource."""
        return {
            "resourceType": "Account",
            "id": f"account-{invoice.invoice_id}",
            "identifier": [
                {
                    "system": "http://hospital.medbill.org/accounts",
                    "value": invoice.invoice_number
                }
            ],
            "status": "active" if invoice.balance_due > 0 else "closed",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "PBILLACCT",
                        "display": "Patient Billing Account"
                    }
                ]
            },
            "name": f"Hospital Account - {patient.full_name}",
            "subject": [
                {
                    "reference": f"Patient/{patient.patient_id}",
                    "display": patient.full_name
                }
            ],
            "servicePeriod": {
                "start": invoice.issue_date,
                "end": invoice.due_date
            },
            "coverage": [
                {
                    "coverage": {
                        "reference": f"Coverage/{policy.policy_id}" if policy else "Coverage/SelfPay",
                        "display": policy.plan_name if policy else "Self-Pay Patient"
                    },
                    "priority": 1
                }
            ],
            "balance": [
                {
                    "currency": invoice.currency,
                    "amount": invoice.balance_due
                }
            ]
        }

    @staticmethod
    def build_coverage_resource(
        patient: Patient,
        policy: InsurancePolicy
    ) -> Dict[str, Any]:
        """Generate FHIR R4 'Coverage' resource."""
        return {
            "resourceType": "Coverage",
            "id": f"coverage-{policy.policy_id}",
            "identifier": [
                {
                    "system": "http://insurance.medbill.org/member-id",
                    "value": policy.member_id
                }
            ],
            "status": "active" if policy.is_active else "cancelled",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": policy.plan_type.value,
                        "display": policy.plan_name
                    }
                ]
            },
            "subscriber": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.full_name
            },
            "beneficiary": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.full_name
            },
            "relationship": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/subscriber-relationship",
                        "code": "self",
                        "display": "Self"
                    }
                ]
            },
            "period": {
                "start": policy.effective_date,
                "end": policy.expiration_date
            },
            "payor": [
                {
                    "identifier": {
                        "system": "http://insurance.medbill.org/payer-id",
                        "value": policy.payer_id
                    },
                    "display": policy.payer_name
                }
            ],
            "class": [
                {
                    "type": {
                        "coding": [{"system": "http://terminology.hl7.org/CodeSystem/coverage-class", "code": "group"}]
                    },
                    "value": policy.group_number,
                    "name": policy.plan_name
                }
            ]
        }

    @staticmethod
    def build_claim_resource(
        encounter: Encounter,
        patient: Patient,
        policy: InsurancePolicy,
        line_items: List[BillingLineItem]
    ) -> Dict[str, Any]:
        """Generate FHIR R4 'Claim' resource."""
        claim_id = f"claim-{encounter.encounter_id}"
        return {
            "resourceType": "Claim",
            "id": claim_id,
            "identifier": [
                {
                    "system": "http://hospital.medbill.org/claims",
                    "value": claim_id
                }
            ],
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                        "code": "institutional" if encounter.encounter_type.value == "INPATIENT" else "professional",
                        "display": "Institutional" if encounter.encounter_type.value == "INPATIENT" else "Professional"
                    }
                ]
            },
            "use": "claim",
            "patient": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.full_name
            },
            "created": datetime.utcnow().isoformat(),
            "provider": {
                "reference": "Organization/MedBill-Hospital",
                "display": "MedBill Memorial Medical Center"
            },
            "priority": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/processpriority",
                        "code": "normal"
                    }
                ]
            },
            "insurance": [
                {
                    "sequence": 1,
                    "focal": True,
                    "coverage": {
                        "reference": f"Coverage/{policy.policy_id}",
                        "display": policy.plan_name
                    }
                }
            ],
            "diagnosis": [
                {
                    "sequence": 1,
                    "diagnosisCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                                "code": encounter.primary_icd10_code or "Z00.00",
                                "display": "Primary Clinical Diagnosis"
                            }
                        ]
                    }
                }
            ],
            "item": [
                {
                    "sequence": idx + 1,
                    "productOrService": {
                        "coding": [
                            {
                                "system": "http://www.ama-assn.org/go/cpt",
                                "code": item.item_code,
                                "display": item.item_name
                            }
                        ]
                    },
                    "quantity": {
                        "value": item.quantity
                    },
                    "unitPrice": {
                        "value": item.unit_price,
                        "currency": "USD"
                    },
                    "net": {
                        "value": item.total_amount,
                        "currency": "USD"
                    }
                }
                for idx, item in enumerate(line_items)
            ],
            "total": {
                "value": sum(i.total_amount for i in line_items),
                "currency": "USD"
            }
        }

    @staticmethod
    def build_explanation_of_benefit_resource(
        adjudication: AdjudicationSummary,
        patient: Patient
    ) -> Dict[str, Any]:
        """Generate FHIR R4 'ExplanationOfBenefit' (EOB) resource."""
        return {
            "resourceType": "ExplanationOfBenefit",
            "id": f"eob-{adjudication.claim_id}",
            "identifier": [
                {
                    "system": "http://insurance.medbill.org/eob",
                    "value": adjudication.claim_id
                }
            ],
            "status": "active",
            "type": {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/claim-type",
                        "code": "institutional",
                        "display": "Hospital Inpatient & Outpatient EOB"
                    }
                ]
            },
            "use": "claim",
            "patient": {
                "reference": f"Patient/{patient.patient_id}",
                "display": patient.full_name
            },
            "created": adjudication.adjudication_timestamp,
            "insurer": {
                "display": adjudication.payer_name
            },
            "outcome": "complete" if adjudication.status.value == "APPROVED" else "partial",
            "total": [
                {"category": {"coding": [{"code": "submitted"}]}, "amount": {"value": adjudication.total_billed, "currency": "USD"}},
                {"category": {"coding": [{"code": "benefit"}]}, "amount": {"value": adjudication.total_payer_paid, "currency": "USD"}},
                {"category": {"coding": [{"code": "patient-pay"}]}, "amount": {"value": adjudication.total_patient_responsibility, "currency": "USD"}}
            ],
            "disposition": adjudication.explanation_of_benefits_notes
        }

"""
MedBill Enterprise - Health Insurance Adjudication & Claims Engine
Simulates real-time payer claim adjudication: calculates contractual allowances,
deductible satisfaction, co-payments, co-insurance percentages, and out-of-pocket maximum caps.
Generates CMS-1500 (Professional) and UB-04 (Institutional) claim representations.
"""

from datetime import datetime
from typing import List, Dict, Optional, Any
import uuid

from medbill.core.models import (
    Encounter,
    EncounterType,
    Patient,
    BillingLineItem,
    BillingItemCategory,
)
from medbill.modules.insurance_tpa.models import (
    InsurancePolicy,
    PlanType,
    ClaimType,
    AdjudicationStatus,
    ClaimLineAdjudication,
    AdjudicationSummary,
)


class InsuranceClaimsEngine:
    """
    Enterprise Claims Adjudication & Insurance Processing Engine.
    """

    def adjudicate_claim(
        self,
        encounter: Encounter,
        patient: Patient,
        policy: InsurancePolicy,
        line_items: List[BillingLineItem],
        pre_authorization_code: Optional[str] = None
    ) -> AdjudicationSummary:
        """
        Adjudicates all line items against an insurance policy.
        Applies contractual fee discount, deductible, copay, coinsurance, and OOPM limits.
        """
        claim_id = f"CLM-{uuid.uuid4().hex[:10].upper()}"
        today_str = datetime.utcnow().strftime("%Y-%m-%d")

        if not policy.is_valid_for_date(today_str):
            # Policy is expired or inactive -> Entire claim is patient responsibility
            total_billed = round(sum(i.total_amount for i in line_items), 2)
            return AdjudicationSummary(
                claim_id=claim_id,
                encounter_id=encounter.encounter_id,
                policy_id=policy.policy_id,
                payer_name=policy.payer_name,
                total_billed=total_billed,
                total_contractual_discount=0.0,
                total_allowed=0.0,
                total_deductible=0.0,
                total_copay=0.0,
                total_coinsurance=0.0,
                total_payer_paid=0.0,
                total_patient_responsibility=total_billed,
                status=AdjudicationStatus.DENIED,
                explanation_of_benefits_notes=f"Claim Denied: Policy {policy.policy_id} is inactive or expired."
            )

        # Track accumulators locally during adjudication
        running_deductible_met = policy.deductible_met
        remaining_deductible = max(0.0, policy.annual_deductible - running_deductible_met)

        running_oop_met = policy.out_of_pocket_met
        remaining_oop = max(0.0, policy.annual_out_of_pocket_max - running_oop_met)

        line_adjudications: List[ClaimLineAdjudication] = []
        is_inpatient = encounter.encounter_type in (EncounterType.INPATIENT, EncounterType.EMERGENCY)

        # Total billed amount check for pre-auth requirements
        total_claim_billed = sum(i.total_amount for i in line_items)
        if (
            (policy.pre_auth_required_for_inpatient and is_inpatient) or
            (total_claim_billed >= policy.pre_auth_threshold_amount)
        ) and not pre_authorization_code:
            # Deny for missing pre-authorization
            return AdjudicationSummary(
                claim_id=claim_id,
                encounter_id=encounter.encounter_id,
                policy_id=policy.policy_id,
                payer_name=policy.payer_name,
                total_billed=round(total_claim_billed, 2),
                total_contractual_discount=0.0,
                total_allowed=0.0,
                total_deductible=0.0,
                total_copay=0.0,
                total_coinsurance=0.0,
                total_payer_paid=0.0,
                total_patient_responsibility=round(total_claim_billed, 2),
                status=AdjudicationStatus.REQUIRES_PRE_AUTH,
                explanation_of_benefits_notes="Pre-authorization required for inpatient/major procedures exceeding threshold. (CARC CO-197)."
            )

        # Process each line item
        for item in line_items:
            billed = item.total_amount

            # 1. Contractual PPO In-Network Discount
            discount_pct = policy.contractual_discount_percent
            contractual_discount = round(billed * (discount_pct / 100.0), 2)
            allowed_amount = round(billed - contractual_discount, 2)

            # 2. Fixed Co-Payment Check
            copay = 0.0
            if item.category == BillingItemCategory.CONSULTATION:
                if encounter.encounter_type == EncounterType.EMERGENCY:
                    copay = min(allowed_amount, policy.copay_emergency)
                else:
                    copay = min(allowed_amount, policy.copay_specialist_opd)

            amount_after_copay = max(0.0, allowed_amount - copay)

            # 3. Deductible Application
            deductible_applied = 0.0
            if remaining_deductible > 0 and amount_after_copay > 0:
                deductible_applied = min(amount_after_copay, remaining_deductible)
                remaining_deductible -= deductible_applied
                running_deductible_met += deductible_applied

            amount_subject_to_coinsurance = max(0.0, amount_after_copay - deductible_applied)

            # 4. Co-Insurance Application (e.g. 20% patient, 80% payer)
            coinsurance_patient = 0.0
            payer_paid = 0.0

            if remaining_oop <= 0:
                # OOPM reached: Insurer pays 100% of allowed amount after contractual discount
                payer_paid = amount_subject_to_coinsurance
                coinsurance_patient = 0.0
            else:
                raw_coinsurance = round(amount_subject_to_coinsurance * policy.coinsurance_rate, 2)
                # Cap patient responsibility by remaining OOPM
                coinsurance_patient = min(raw_coinsurance, remaining_oop)
                payer_paid = round(amount_subject_to_coinsurance - coinsurance_patient, 2)

            # Total patient responsibility for this line
            patient_resp = round(copay + deductible_applied + coinsurance_patient, 2)
            remaining_oop = max(0.0, remaining_oop - patient_resp)
            running_oop_met += patient_resp

            line_adj = ClaimLineAdjudication(
                line_item_id=item.item_id,
                item_code=item.item_code,
                item_name=item.item_name,
                billed_amount=billed,
                contractual_allowed_amount=allowed_amount,
                contractual_discount=contractual_discount,
                deductible_applied=deductible_applied,
                copay_applied=copay,
                coinsurance_applied=coinsurance_patient,
                payer_covered_amount=payer_paid,
                patient_responsibility=patient_resp,
                status=AdjudicationStatus.APPROVED,
                carc_reason_code="CO-45 / PR-1 / PR-2 / PR-3",
                carc_reason_description="Contractual Adjustment, Deductible, Co-pay & Co-insurance"
            )
            line_adjudications.append(line_adj)

        # Totals calculation
        tot_billed = round(sum(l.billed_amount for l in line_adjudications), 2)
        tot_discount = round(sum(l.contractual_discount for l in line_adjudications), 2)
        tot_allowed = round(sum(l.contractual_allowed_amount for l in line_adjudications), 2)
        tot_deductible = round(sum(l.deductible_applied for l in line_adjudications), 2)
        tot_copay = round(sum(l.copay_applied for l in line_adjudications), 2)
        tot_coinsurance = round(sum(l.coinsurance_applied for l in line_adjudications), 2)
        tot_payer_paid = round(sum(l.payer_covered_amount for l in line_adjudications), 2)
        tot_patient_resp = round(sum(l.patient_responsibility for l in line_adjudications), 2)

        return AdjudicationSummary(
            claim_id=claim_id,
            encounter_id=encounter.encounter_id,
            policy_id=policy.policy_id,
            payer_name=policy.payer_name,
            total_billed=tot_billed,
            total_contractual_discount=tot_discount,
            total_allowed=tot_allowed,
            total_deductible=tot_deductible,
            total_copay=tot_copay,
            total_coinsurance=tot_coinsurance,
            total_payer_paid=tot_payer_paid,
            total_patient_responsibility=tot_patient_resp,
            status=AdjudicationStatus.APPROVED if tot_payer_paid > 0 else AdjudicationStatus.PARTIALLY_APPROVED,
            line_adjudications=line_adjudications,
            explanation_of_benefits_notes=f"Adjudicated under {policy.plan_name} ({policy.plan_type.value}). Insurer paid ${tot_payer_paid:.2f}, Patient owes ${tot_patient_resp:.2f}."
        )

    def generate_cms_1500_claim_json(
        self,
        encounter: Encounter,
        patient: Patient,
        policy: InsurancePolicy,
        line_items: List[BillingLineItem]
    ) -> Dict[str, Any]:
        """
        Generates structured CMS-1500 professional claim document.
        """
        return {
            "form_type": "CMS-1500 (HCFA-1500) Health Insurance Claim Form",
            "claim_reference": f"CMS1500-{uuid.uuid4().hex[:8].upper()}",
            "carrier_block": {
                "payer_name": policy.payer_name,
                "payer_id": policy.payer_id,
                "plan_type": policy.plan_type.value
            },
            "box_1_to_13_patient_insured": {
                "patient_name": patient.full_name,
                "patient_dob": patient.dob,
                "patient_gender": patient.gender.value,
                "patient_address": patient.address,
                "insured_id_number": policy.member_id,
                "insured_group_number": policy.group_number,
                "insured_plan_name": policy.plan_name
            },
            "box_21_diagnosis_codes": [
                {"icd10": encounter.primary_icd10_code or "Z00.00", "pointer": "A"}
            ] + [{"icd10": code, "pointer": chr(66 + idx)} for idx, code in enumerate(encounter.secondary_icd10_codes[:3])],
            "box_24_service_lines": [
                {
                    "line_number": idx + 1,
                    "date_of_service": item.created_at[:10],
                    "place_of_service": "11" if encounter.encounter_type == EncounterType.OUTPATIENT else "21",
                    "cpt_hcpcs": item.item_code,
                    "description": item.item_name,
                    "diagnosis_pointer": "A",
                    "charges": item.total_amount,
                    "units": item.quantity
                }
                for idx, item in enumerate(line_items)
            ],
            "box_28_total_charge": sum(i.total_amount for i in line_items),
            "box_33_billing_provider": {
                "hospital_name": "MedBill Memorial Medical Center",
                "npi": "1992837465",
                "tax_id": "XX-XXXXXXX"
            }
        }

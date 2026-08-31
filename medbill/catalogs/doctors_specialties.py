"""
MedBill Enterprise Catalogs - Doctor Specialties & Consultation Tariff Matrix
Defines healthcare clinical specialties, default consultation fees across seniority ranks,
emergency multipliers, and follow-up validity rules.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from medbill.core.models import DoctorRank


@dataclass(frozen=True)
class SpecialtyTariffSchedule:
    specialty_code: str
    specialty_name: str
    department_id: str
    base_opd_fee: float
    base_ipd_visit_fee: float
    emergency_oncall_fee: float
    telemedicine_fee: float
    follow_up_validity_days: int  # Standard days within which follow-up is free or discounted
    follow_up_discount_percent: float  # 100% means free follow-up
    rank_multipliers: Dict[DoctorRank, float] = field(default_factory=lambda: {
        DoctorRank.JUNIOR_RESIDENT: 0.70,
        DoctorRank.ATTENDING_PHYSICIAN: 1.00,
        DoctorRank.SENIOR_CONSULTANT: 1.40,
        DoctorRank.DEPARTMENT_HEAD: 1.80,
        DoctorRank.EMERITUS_PROFESSOR: 2.20
    })


# Master Specialty Schedules
SPECIALTY_CATALOG: Dict[str, SpecialtyTariffSchedule] = {
    "GEN_MED": SpecialtyTariffSchedule(
        specialty_code="GEN_MED",
        specialty_name="Internal Medicine / General Physician",
        department_id="DEPT_MED",
        base_opd_fee=75.00,
        base_ipd_visit_fee=65.00,
        emergency_oncall_fee=150.00,
        telemedicine_fee=60.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "CARDIO": SpecialtyTariffSchedule(
        specialty_code="CARDIO",
        specialty_name="Cardiology & Interventional Cardiology",
        department_id="DEPT_CARDIO",
        base_opd_fee=150.00,
        base_ipd_visit_fee=125.00,
        emergency_oncall_fee=300.00,
        telemedicine_fee=120.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "CTVS": SpecialtyTariffSchedule(
        specialty_code="CTVS",
        specialty_name="Cardiothoracic & Vascular Surgery",
        department_id="DEPT_CTVS",
        base_opd_fee=180.00,
        base_ipd_visit_fee=150.00,
        emergency_oncall_fee=350.00,
        telemedicine_fee=140.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=100.00
    ),
    "NEURO_MED": SpecialtyTariffSchedule(
        specialty_code="NEURO_MED",
        specialty_name="Neurology",
        department_id="DEPT_NEURO",
        base_opd_fee=140.00,
        base_ipd_visit_fee=120.00,
        emergency_oncall_fee=280.00,
        telemedicine_fee=115.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "NEURO_SURG": SpecialtyTariffSchedule(
        specialty_code="NEURO_SURG",
        specialty_name="Neurosurgery & Spine Surgery",
        department_id="DEPT_NEURO_SURG",
        base_opd_fee=190.00,
        base_ipd_visit_fee=160.00,
        emergency_oncall_fee=380.00,
        telemedicine_fee=150.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=100.00
    ),
    "ORTHO": SpecialtyTariffSchedule(
        specialty_code="ORTHO",
        specialty_name="Orthopedics & Joint Replacement",
        department_id="DEPT_ORTHO",
        base_opd_fee=120.00,
        base_ipd_visit_fee=100.00,
        emergency_oncall_fee=250.00,
        telemedicine_fee=95.00,
        follow_up_validity_days=10,
        follow_up_discount_percent=100.00
    ),
    "ONCO_MED": SpecialtyTariffSchedule(
        specialty_code="ONCO_MED",
        specialty_name="Medical Oncology",
        department_id="DEPT_ONCO",
        base_opd_fee=160.00,
        base_ipd_visit_fee=135.00,
        emergency_oncall_fee=300.00,
        telemedicine_fee=130.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=100.00
    ),
    "ONCO_SURG": SpecialtyTariffSchedule(
        specialty_code="ONCO_SURG",
        specialty_name="Surgical Oncology",
        department_id="DEPT_ONCO",
        base_opd_fee=175.00,
        base_ipd_visit_fee=145.00,
        emergency_oncall_fee=340.00,
        telemedicine_fee=140.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=100.00
    ),
    "GASTRO": SpecialtyTariffSchedule(
        specialty_code="GASTRO",
        specialty_name="Gastroenterology & Hepatology",
        department_id="DEPT_GASTRO",
        base_opd_fee=130.00,
        base_ipd_visit_fee=110.00,
        emergency_oncall_fee=260.00,
        telemedicine_fee=100.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "NEPHRO": SpecialtyTariffSchedule(
        specialty_code="NEPHRO",
        specialty_name="Nephrology & Renal Transplant",
        department_id="DEPT_NEPHRO",
        base_opd_fee=135.00,
        base_ipd_visit_fee=115.00,
        emergency_oncall_fee=270.00,
        telemedicine_fee=105.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "PULMO": SpecialtyTariffSchedule(
        specialty_code="PULMO",
        specialty_name="Pulmonology & Respiratory Medicine",
        department_id="DEPT_PULMO",
        base_opd_fee=125.00,
        base_ipd_visit_fee=105.00,
        emergency_oncall_fee=250.00,
        telemedicine_fee=95.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "PEDIATRICS": SpecialtyTariffSchedule(
        specialty_code="PEDIATRICS",
        specialty_name="Pediatrics & Neonatology",
        department_id="DEPT_PED",
        base_opd_fee=95.00,
        base_ipd_visit_fee=85.00,
        emergency_oncall_fee=200.00,
        telemedicine_fee=75.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "OBGYN": SpecialtyTariffSchedule(
        specialty_code="OBGYN",
        specialty_name="Obstetrics & Gynecology",
        department_id="DEPT_OBGYN",
        base_opd_fee=110.00,
        base_ipd_visit_fee=95.00,
        emergency_oncall_fee=240.00,
        telemedicine_fee=85.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "ENDOCRIN": SpecialtyTariffSchedule(
        specialty_code="ENDOCRIN",
        specialty_name="Endocrinology & Diabetology",
        department_id="DEPT_ENDO",
        base_opd_fee=115.00,
        base_ipd_visit_fee=95.00,
        emergency_oncall_fee=220.00,
        telemedicine_fee=90.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=100.00
    ),
    "PSYCHIATRY": SpecialtyTariffSchedule(
        specialty_code="PSYCHIATRY",
        specialty_name="Psychiatry & Behavioral Health",
        department_id="DEPT_PSYCH",
        base_opd_fee=130.00,
        base_ipd_visit_fee=110.00,
        emergency_oncall_fee=250.00,
        telemedicine_fee=110.00,
        follow_up_validity_days=14,
        follow_up_discount_percent=50.00
    ),
    "DERMA": SpecialtyTariffSchedule(
        specialty_code="DERMA",
        specialty_name="Dermatology & Cosmetology",
        department_id="DEPT_DERMA",
        base_opd_fee=90.00,
        base_ipd_visit_fee=75.00,
        emergency_oncall_fee=180.00,
        telemedicine_fee=75.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "ENT": SpecialtyTariffSchedule(
        specialty_code="ENT",
        specialty_name="Otorhinolaryngology (ENT)",
        department_id="DEPT_ENT",
        base_opd_fee=95.00,
        base_ipd_visit_fee=80.00,
        emergency_oncall_fee=200.00,
        telemedicine_fee=75.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "OPHTHAL": SpecialtyTariffSchedule(
        specialty_code="OPHTHAL",
        specialty_name="Ophthalmology",
        department_id="DEPT_EYE",
        base_opd_fee=95.00,
        base_ipd_visit_fee=80.00,
        emergency_oncall_fee=200.00,
        telemedicine_fee=75.00,
        follow_up_validity_days=7,
        follow_up_discount_percent=100.00
    ),
    "EMERGENCY_MED": SpecialtyTariffSchedule(
        specialty_code="EMERGENCY_MED",
        specialty_name="Emergency & Trauma Medicine",
        department_id="DEPT_ER",
        base_opd_fee=120.00,
        base_ipd_visit_fee=110.00,
        emergency_oncall_fee=250.00,
        telemedicine_fee=100.00,
        follow_up_validity_days=3,
        follow_up_discount_percent=100.00
    ),
    "CRITICAL_CARE": SpecialtyTariffSchedule(
        specialty_code="CRITICAL_CARE",
        specialty_name="Intensive & Critical Care Medicine",
        department_id="DEPT_ICU",
        base_opd_fee=160.00,
        base_ipd_visit_fee=175.00,
        emergency_oncall_fee=350.00,
        telemedicine_fee=140.00,
        follow_up_validity_days=3,
        follow_up_discount_percent=100.00
    )
}


def get_specialty_schedule(specialty_code: str) -> Optional[SpecialtyTariffSchedule]:
    """Retrieve specialty tariff schedule."""
    return SPECIALTY_CATALOG.get(specialty_code)

"""
MedBill Enterprise Catalogs - Hospital Bed & Room Categories Master Catalog
Defines comprehensive inpatient ward tiers, intensive care units, daily/hourly base tariffs,
nursing charges, biomedical waste handling, oxygen, ventilator and continuous telemetry tariffs.
"""

from dataclasses import dataclass
from typing import Dict, Optional
from medbill.core.models import RoomCategoryType


@dataclass(frozen=True)
class RoomTariffSchedule:
    category: RoomCategoryType
    name: str
    description: str
    daily_base_rate: float
    hourly_rate: float
    nursing_daily_charge: float
    resident_doctor_daily_charge: float
    biomedical_waste_daily_charge: float
    housekeeping_daily_charge: float
    oxygen_hourly_rate: float
    ventilator_hourly_rate: float
    telemetry_monitoring_hourly_rate: float
    infusion_pump_daily_rate: float
    air_conditioning_included: bool = True
    diet_included: bool = True
    max_accompanying_attendants: int = 1


# Master Room Tariff Schedules
ROOM_TARIFF_CATALOG: Dict[RoomCategoryType, RoomTariffSchedule] = {
    RoomCategoryType.GENERAL_WARD_MALE: RoomTariffSchedule(
        category=RoomCategoryType.GENERAL_WARD_MALE,
        name="General Male Ward (Multi-Bed)",
        description="Shared air-conditioned general inpatient ward with standard nursing care.",
        daily_base_rate=450.00,
        hourly_rate=25.00,
        nursing_daily_charge=120.00,
        resident_doctor_daily_charge=80.00,
        biomedical_waste_daily_charge=25.00,
        housekeeping_daily_charge=25.00,
        oxygen_hourly_rate=15.00,
        ventilator_hourly_rate=75.00,
        telemetry_monitoring_hourly_rate=20.00,
        infusion_pump_daily_rate=30.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.GENERAL_WARD_FEMALE: RoomTariffSchedule(
        category=RoomCategoryType.GENERAL_WARD_FEMALE,
        name="General Female Ward (Multi-Bed)",
        description="Shared air-conditioned female inpatient ward with dedicated nursing staff.",
        daily_base_rate=450.00,
        hourly_rate=25.00,
        nursing_daily_charge=120.00,
        resident_doctor_daily_charge=80.00,
        biomedical_waste_daily_charge=25.00,
        housekeeping_daily_charge=25.00,
        oxygen_hourly_rate=15.00,
        ventilator_hourly_rate=75.00,
        telemetry_monitoring_hourly_rate=20.00,
        infusion_pump_daily_rate=30.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.SEMI_PRIVATE_ROOM: RoomTariffSchedule(
        category=RoomCategoryType.SEMI_PRIVATE_ROOM,
        name="Semi-Private Twin Sharing Room",
        description="Twin sharing room with privacy partition, attached washroom and dedicated nurse buzzer.",
        daily_base_rate=850.00,
        hourly_rate=45.00,
        nursing_daily_charge=180.00,
        resident_doctor_daily_charge=120.00,
        biomedical_waste_daily_charge=35.00,
        housekeeping_daily_charge=40.00,
        oxygen_hourly_rate=18.00,
        ventilator_hourly_rate=85.00,
        telemetry_monitoring_hourly_rate=25.00,
        infusion_pump_daily_rate=40.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.PRIVATE_DELUXE: RoomTariffSchedule(
        category=RoomCategoryType.PRIVATE_DELUXE,
        name="Single Private Deluxe Room",
        description="Individual private room with motorized electronic bed, attendant couch, LED TV and en-suite bathroom.",
        daily_base_rate=1450.00,
        hourly_rate=75.00,
        nursing_daily_charge=260.00,
        resident_doctor_daily_charge=180.00,
        biomedical_waste_daily_charge=50.00,
        housekeeping_daily_charge=60.00,
        oxygen_hourly_rate=22.00,
        ventilator_hourly_rate=95.00,
        telemetry_monitoring_hourly_rate=30.00,
        infusion_pump_daily_rate=50.00,
        max_accompanying_attendants=2
    ),
    RoomCategoryType.SUPER_DELUXE_SUITE: RoomTariffSchedule(
        category=RoomCategoryType.SUPER_DELUXE_SUITE,
        name="Super Deluxe Executive Suite",
        description="Spacious two-room suite with patient care area, separate attendant living lounge, kitchenette and dedicated concierge.",
        daily_base_rate=2400.00,
        hourly_rate=120.00,
        nursing_daily_charge=400.00,
        resident_doctor_daily_charge=250.00,
        biomedical_waste_daily_charge=70.00,
        housekeeping_daily_charge=100.00,
        oxygen_hourly_rate=25.00,
        ventilator_hourly_rate=110.00,
        telemetry_monitoring_hourly_rate=35.00,
        infusion_pump_daily_rate=60.00,
        max_accompanying_attendants=3
    ),
    RoomCategoryType.PRESIDENTIAL_SUITE: RoomTariffSchedule(
        category=RoomCategoryType.PRESIDENTIAL_SUITE,
        name="Presidential VIP Luxury Suite",
        description="Luxury hospital suite with private nurse, dining room, executive boardroom, security access and premium amenities.",
        daily_base_rate=4500.00,
        hourly_rate=220.00,
        nursing_daily_charge=750.00,
        resident_doctor_daily_charge=450.00,
        biomedical_waste_daily_charge=100.00,
        housekeeping_daily_charge=200.00,
        oxygen_hourly_rate=30.00,
        ventilator_hourly_rate=130.00,
        telemetry_monitoring_hourly_rate=45.00,
        infusion_pump_daily_rate=80.00,
        max_accompanying_attendants=4
    ),
    RoomCategoryType.INTENSIVE_CARE_UNIT_ICU: RoomTariffSchedule(
        category=RoomCategoryType.INTENSIVE_CARE_UNIT_ICU,
        name="Multi-Disciplinary Intensive Care Unit (ICU)",
        description="Level-3 tertiary ICU with 1:1 dedicated critical care nursing, invasive arterial lines, central monitoring and high-flow capability.",
        daily_base_rate=3200.00,
        hourly_rate=160.00,
        nursing_daily_charge=850.00,
        resident_doctor_daily_charge=550.00,
        biomedical_waste_daily_charge=120.00,
        housekeeping_daily_charge=120.00,
        oxygen_hourly_rate=35.00,
        ventilator_hourly_rate=125.00,
        telemetry_monitoring_hourly_rate=50.00,
        infusion_pump_daily_rate=75.00,
        max_accompanying_attendants=0
    ),
    RoomCategoryType.CORONARY_CARE_UNIT_CCU: RoomTariffSchedule(
        category=RoomCategoryType.CORONARY_CARE_UNIT_CCU,
        name="Coronary Care Unit (CCU / ICCU)",
        description="Specialized cardiac ICU equipped for acute myocardial infarction, arrhythmias, IABP, temporary pacemakers and hemodynamics.",
        daily_base_rate=3400.00,
        hourly_rate=170.00,
        nursing_daily_charge=880.00,
        resident_doctor_daily_charge=580.00,
        biomedical_waste_daily_charge=125.00,
        housekeeping_daily_charge=125.00,
        oxygen_hourly_rate=35.00,
        ventilator_hourly_rate=125.00,
        telemetry_monitoring_hourly_rate=55.00,
        infusion_pump_daily_rate=75.00,
        max_accompanying_attendants=0
    ),
    RoomCategoryType.NEONATAL_ICU_NICU: RoomTariffSchedule(
        category=RoomCategoryType.NEONATAL_ICU_NICU,
        name="Neonatal Intensive Care Unit (NICU Level III)",
        description="Specialized neonatal care with servo-controlled incubators, phototherapy, neonatal high-frequency oscillatory ventilation and TPN.",
        daily_base_rate=2900.00,
        hourly_rate=145.00,
        nursing_daily_charge=800.00,
        resident_doctor_daily_charge=500.00,
        biomedical_waste_daily_charge=110.00,
        housekeeping_daily_charge=100.00,
        oxygen_hourly_rate=30.00,
        ventilator_hourly_rate=120.00,
        telemetry_monitoring_hourly_rate=45.00,
        infusion_pump_daily_rate=70.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.PEDIATRIC_ICU_PICU: RoomTariffSchedule(
        category=RoomCategoryType.PEDIATRIC_ICU_PICU,
        name="Pediatric Intensive Care Unit (PICU)",
        description="Comprehensive pediatric critical care unit for infants and children with multi-organ failure and post-cardiac surgery recovery.",
        daily_base_rate=3000.00,
        hourly_rate=150.00,
        nursing_daily_charge=820.00,
        resident_doctor_daily_charge=520.00,
        biomedical_waste_daily_charge=115.00,
        housekeeping_daily_charge=110.00,
        oxygen_hourly_rate=32.00,
        ventilator_hourly_rate=120.00,
        telemetry_monitoring_hourly_rate=48.00,
        infusion_pump_daily_rate=70.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.HIGH_DEPENDENCY_UNIT_HDU: RoomTariffSchedule(
        category=RoomCategoryType.HIGH_DEPENDENCY_UNIT_HDU,
        name="High Dependency Unit (HDU / Step-Down)",
        description="Intermediate care unit for patients transitioning out of intensive care who require high-ratio nursing and continuous telemetry.",
        daily_base_rate=1950.00,
        hourly_rate=95.00,
        nursing_daily_charge=450.00,
        resident_doctor_daily_charge=300.00,
        biomedical_waste_daily_charge=75.00,
        housekeeping_daily_charge=80.00,
        oxygen_hourly_rate=25.00,
        ventilator_hourly_rate=100.00,
        telemetry_monitoring_hourly_rate=35.00,
        infusion_pump_daily_rate=55.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.ISOLATION_WARD: RoomTariffSchedule(
        category=RoomCategoryType.ISOLATION_WARD,
        name="Negative Pressure Infectious Isolation Ward",
        description="Negative pressure isolation suite with HEPA filtration, dedicated anteroom and full PPE barrier nursing.",
        daily_base_rate=2200.00,
        hourly_rate=110.00,
        nursing_daily_charge=550.00,
        resident_doctor_daily_charge=350.00,
        biomedical_waste_daily_charge=150.00,
        housekeeping_daily_charge=120.00,
        oxygen_hourly_rate=28.00,
        ventilator_hourly_rate=115.00,
        telemetry_monitoring_hourly_rate=40.00,
        infusion_pump_daily_rate=60.00,
        max_accompanying_attendants=0
    ),
    RoomCategoryType.DAYCARE_BED: RoomTariffSchedule(
        category=RoomCategoryType.DAYCARE_BED,
        name="Daycare Surgery / Chemotherapy Bed",
        description="Short-stay ambulatory care bed for day procedures, minor surgery, endoscopy and chemotherapy infusions up to 8 hours.",
        daily_base_rate=650.00,
        hourly_rate=55.00,
        nursing_daily_charge=150.00,
        resident_doctor_daily_charge=90.00,
        biomedical_waste_daily_charge=30.00,
        housekeeping_daily_charge=30.00,
        oxygen_hourly_rate=18.00,
        ventilator_hourly_rate=80.00,
        telemetry_monitoring_hourly_rate=25.00,
        infusion_pump_daily_rate=35.00,
        max_accompanying_attendants=1
    ),
    RoomCategoryType.EMERGENCY_OBSERVATION: RoomTariffSchedule(
        category=RoomCategoryType.EMERGENCY_OBSERVATION,
        name="Emergency Department Observation Bed",
        description="Emergency triage observation bed for clinical monitoring up to 24 hours prior to inpatient admission or safe discharge.",
        daily_base_rate=750.00,
        hourly_rate=60.00,
        nursing_daily_charge=200.00,
        resident_doctor_daily_charge=150.00,
        biomedical_waste_daily_charge=40.00,
        housekeeping_daily_charge=40.00,
        oxygen_hourly_rate=20.00,
        ventilator_hourly_rate=90.00,
        telemetry_monitoring_hourly_rate=30.00,
        infusion_pump_daily_rate=40.00,
        max_accompanying_attendants=1
    )
}


def get_room_schedule(category: RoomCategoryType) -> Optional[RoomTariffSchedule]:
    """Retrieve room schedule by category enum."""
    return ROOM_TARIFF_CATALOG.get(category)

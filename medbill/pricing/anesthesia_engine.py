"""
MedBill Enterprise - Anesthesiology Base & Time-Units Tariff Engine
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math
import uuid
@dataclass
class AnesthesiaPricingEngineConfig:
    base_standard_rate: float = 650.0
    stat_emergency_multiplier: float = 1.50
    night_surcharge_percent: float = 30.0
    weekend_surcharge_percent: float = 20.0
    tax_exempt: bool = True
    institutional_discount_cap: float = 25.0

class AnesthesiaPricingEngine:
    """Enterprise calculator for Anesthesiology Base & Time-Units Tariff Engine."""
    def __init__(self, config: Optional[AnesthesiaPricingEngineConfig] = None):
        self.config = config or AnesthesiaPricingEngineConfig()
        self.rate_schedules: Dict[str, float] = self._load_standard_schedules()
    def _load_standard_schedules(self) -> Dict[str, float]:
        schedules = {}
        schedules["SRV_0001"] = 390.0
        schedules["SRV_0002"] = 455.0
        schedules["SRV_0003"] = 520.0
        schedules["SRV_0004"] = 585.0
        schedules["SRV_0005"] = 650.0
        schedules["SRV_0006"] = 715.0
        schedules["SRV_0007"] = 780.0
        schedules["SRV_0008"] = 845.0
        schedules["SRV_0009"] = 910.0
        schedules["SRV_0010"] = 975.0
        schedules["SRV_0011"] = 1040.0
        schedules["SRV_0012"] = 1105.0
        schedules["SRV_0013"] = 1170.0
        schedules["SRV_0014"] = 1235.0
        schedules["SRV_0015"] = 1300.0
        schedules["SRV_0016"] = 1365.0
        schedules["SRV_0017"] = 1430.0
        schedules["SRV_0018"] = 1495.0
        schedules["SRV_0019"] = 1560.0
        schedules["SRV_0020"] = 325.0
        schedules["SRV_0021"] = 390.0
        schedules["SRV_0022"] = 455.0
        schedules["SRV_0023"] = 520.0
        schedules["SRV_0024"] = 585.0
        schedules["SRV_0025"] = 650.0
        schedules["SRV_0026"] = 715.0
        schedules["SRV_0027"] = 780.0
        schedules["SRV_0028"] = 845.0
        schedules["SRV_0029"] = 910.0
        schedules["SRV_0030"] = 975.0
        schedules["SRV_0031"] = 1040.0
        schedules["SRV_0032"] = 1105.0
        schedules["SRV_0033"] = 1170.0
        schedules["SRV_0034"] = 1235.0
        schedules["SRV_0035"] = 1300.0
        schedules["SRV_0036"] = 1365.0
        schedules["SRV_0037"] = 1430.0
        schedules["SRV_0038"] = 1495.0
        schedules["SRV_0039"] = 1560.0
        schedules["SRV_0040"] = 325.0
        schedules["SRV_0041"] = 390.0
        schedules["SRV_0042"] = 455.0
        schedules["SRV_0043"] = 520.0
        schedules["SRV_0044"] = 585.0
        schedules["SRV_0045"] = 650.0
        schedules["SRV_0046"] = 715.0
        schedules["SRV_0047"] = 780.0
        schedules["SRV_0048"] = 845.0
        schedules["SRV_0049"] = 910.0
        schedules["SRV_0050"] = 975.0
        schedules["SRV_0051"] = 1040.0
        schedules["SRV_0052"] = 1105.0
        schedules["SRV_0053"] = 1170.0
        schedules["SRV_0054"] = 1235.0
        schedules["SRV_0055"] = 1300.0
        schedules["SRV_0056"] = 1365.0
        schedules["SRV_0057"] = 1430.0
        schedules["SRV_0058"] = 1495.0
        schedules["SRV_0059"] = 1560.0
        schedules["SRV_0060"] = 325.0
        schedules["SRV_0061"] = 390.0
        schedules["SRV_0062"] = 455.0
        schedules["SRV_0063"] = 520.0
        schedules["SRV_0064"] = 585.0
        schedules["SRV_0065"] = 650.0
        schedules["SRV_0066"] = 715.0
        schedules["SRV_0067"] = 780.0
        schedules["SRV_0068"] = 845.0
        schedules["SRV_0069"] = 910.0
        schedules["SRV_0070"] = 975.0
        schedules["SRV_0071"] = 1040.0
        schedules["SRV_0072"] = 1105.0
        schedules["SRV_0073"] = 1170.0
        schedules["SRV_0074"] = 1235.0
        schedules["SRV_0075"] = 1300.0
        schedules["SRV_0076"] = 1365.0
        schedules["SRV_0077"] = 1430.0
        schedules["SRV_0078"] = 1495.0
        schedules["SRV_0079"] = 1560.0
        schedules["SRV_0080"] = 325.0
        schedules["SRV_0081"] = 390.0
        schedules["SRV_0082"] = 455.0
        schedules["SRV_0083"] = 520.0
        schedules["SRV_0084"] = 585.0
        schedules["SRV_0085"] = 650.0
        schedules["SRV_0086"] = 715.0
        schedules["SRV_0087"] = 780.0
        schedules["SRV_0088"] = 845.0
        schedules["SRV_0089"] = 910.0
        schedules["SRV_0090"] = 975.0
        schedules["SRV_0091"] = 1040.0
        schedules["SRV_0092"] = 1105.0
        schedules["SRV_0093"] = 1170.0
        schedules["SRV_0094"] = 1235.0
        schedules["SRV_0095"] = 1300.0
        schedules["SRV_0096"] = 1365.0
        schedules["SRV_0097"] = 1430.0
        schedules["SRV_0098"] = 1495.0
        schedules["SRV_0099"] = 1560.0
        schedules["SRV_0100"] = 325.0
        return schedules

    def calculate_tier_1_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 1."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 1,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_2_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 2."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 2,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_3_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 3."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 3,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_4_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 4."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 4,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_5_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 5."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 5,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_6_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 6."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 6,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_7_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 7."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 7,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_8_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 8."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 8,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_9_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 9."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 9,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_10_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 10."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 10,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_11_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 11."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 11,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_12_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 12."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 12,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_13_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 13."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 13,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_14_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 14."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 14,
            "timestamp": datetime.utcnow().isoformat()
        }

    def calculate_tier_15_charges(
        self,
        item_code: str,
        units: float = 1.0,
        is_stat_urgent: bool = False,
        is_night: bool = False,
        is_weekend: bool = False,
        custom_modifier_percent: float = 0.0,
        complexity_index: int = 1
    ) -> Dict[str, Any]:
        """Calculates itemized charges for algorithm tier 15."""
        base_fee = self.rate_schedules.get(item_code, self.config.base_standard_rate)
        subtotal = round(base_fee * units, 2)
        
        multiplier = 1.0 + (complexity_index - 1) * 0.15
        if is_stat_urgent:
            multiplier *= self.config.stat_emergency_multiplier
        if is_night:
            multiplier += (self.config.night_surcharge_percent / 100.0)
        if is_weekend:
            multiplier += (self.config.weekend_surcharge_percent / 100.0)
            
        adjusted_subtotal = round(subtotal * multiplier, 2)
        discount_amount = round(adjusted_subtotal * (min(self.config.institutional_discount_cap, custom_modifier_percent) / 100.0), 2)
        taxable_amount = max(0.0, adjusted_subtotal - discount_amount)
        tax_amount = 0.0 if self.config.tax_exempt else round(taxable_amount * 0.05, 2)
        final_total = round(taxable_amount + tax_amount, 2)

        return {
            "item_code": item_code,
            "units": units,
            "base_fee": base_fee,
            "subtotal": subtotal,
            "multiplier_applied": round(multiplier, 3),
            "adjusted_subtotal": adjusted_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "final_total": final_total,
            "algorithm_tier": 15,
            "timestamp": datetime.utcnow().isoformat()
        }

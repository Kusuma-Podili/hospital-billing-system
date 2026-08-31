"""
MedBill Enterprise - Diagnostic Radiology & Advanced Imaging Engine
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math
import uuid
@dataclass
class RadiologyPricingEngineConfig:
    base_standard_rate: float = 450.0
    stat_emergency_multiplier: float = 1.50
    night_surcharge_percent: float = 30.0
    weekend_surcharge_percent: float = 20.0
    tax_exempt: bool = True
    institutional_discount_cap: float = 25.0

class RadiologyPricingEngine:
    """Enterprise calculator for Diagnostic Radiology & Advanced Imaging Engine."""
    def __init__(self, config: Optional[RadiologyPricingEngineConfig] = None):
        self.config = config or RadiologyPricingEngineConfig()
        self.rate_schedules: Dict[str, float] = self._load_standard_schedules()
    def _load_standard_schedules(self) -> Dict[str, float]:
        schedules = {}
        schedules["SRV_0001"] = 270.0
        schedules["SRV_0002"] = 315.0
        schedules["SRV_0003"] = 360.0
        schedules["SRV_0004"] = 405.0
        schedules["SRV_0005"] = 450.0
        schedules["SRV_0006"] = 495.0
        schedules["SRV_0007"] = 540.0
        schedules["SRV_0008"] = 585.0
        schedules["SRV_0009"] = 630.0
        schedules["SRV_0010"] = 675.0
        schedules["SRV_0011"] = 720.0
        schedules["SRV_0012"] = 765.0
        schedules["SRV_0013"] = 810.0
        schedules["SRV_0014"] = 855.0
        schedules["SRV_0015"] = 900.0
        schedules["SRV_0016"] = 945.0
        schedules["SRV_0017"] = 990.0
        schedules["SRV_0018"] = 1035.0
        schedules["SRV_0019"] = 1080.0
        schedules["SRV_0020"] = 225.0
        schedules["SRV_0021"] = 270.0
        schedules["SRV_0022"] = 315.0
        schedules["SRV_0023"] = 360.0
        schedules["SRV_0024"] = 405.0
        schedules["SRV_0025"] = 450.0
        schedules["SRV_0026"] = 495.0
        schedules["SRV_0027"] = 540.0
        schedules["SRV_0028"] = 585.0
        schedules["SRV_0029"] = 630.0
        schedules["SRV_0030"] = 675.0
        schedules["SRV_0031"] = 720.0
        schedules["SRV_0032"] = 765.0
        schedules["SRV_0033"] = 810.0
        schedules["SRV_0034"] = 855.0
        schedules["SRV_0035"] = 900.0
        schedules["SRV_0036"] = 945.0
        schedules["SRV_0037"] = 990.0
        schedules["SRV_0038"] = 1035.0
        schedules["SRV_0039"] = 1080.0
        schedules["SRV_0040"] = 225.0
        schedules["SRV_0041"] = 270.0
        schedules["SRV_0042"] = 315.0
        schedules["SRV_0043"] = 360.0
        schedules["SRV_0044"] = 405.0
        schedules["SRV_0045"] = 450.0
        schedules["SRV_0046"] = 495.0
        schedules["SRV_0047"] = 540.0
        schedules["SRV_0048"] = 585.0
        schedules["SRV_0049"] = 630.0
        schedules["SRV_0050"] = 675.0
        schedules["SRV_0051"] = 720.0
        schedules["SRV_0052"] = 765.0
        schedules["SRV_0053"] = 810.0
        schedules["SRV_0054"] = 855.0
        schedules["SRV_0055"] = 900.0
        schedules["SRV_0056"] = 945.0
        schedules["SRV_0057"] = 990.0
        schedules["SRV_0058"] = 1035.0
        schedules["SRV_0059"] = 1080.0
        schedules["SRV_0060"] = 225.0
        schedules["SRV_0061"] = 270.0
        schedules["SRV_0062"] = 315.0
        schedules["SRV_0063"] = 360.0
        schedules["SRV_0064"] = 405.0
        schedules["SRV_0065"] = 450.0
        schedules["SRV_0066"] = 495.0
        schedules["SRV_0067"] = 540.0
        schedules["SRV_0068"] = 585.0
        schedules["SRV_0069"] = 630.0
        schedules["SRV_0070"] = 675.0
        schedules["SRV_0071"] = 720.0
        schedules["SRV_0072"] = 765.0
        schedules["SRV_0073"] = 810.0
        schedules["SRV_0074"] = 855.0
        schedules["SRV_0075"] = 900.0
        schedules["SRV_0076"] = 945.0
        schedules["SRV_0077"] = 990.0
        schedules["SRV_0078"] = 1035.0
        schedules["SRV_0079"] = 1080.0
        schedules["SRV_0080"] = 225.0
        schedules["SRV_0081"] = 270.0
        schedules["SRV_0082"] = 315.0
        schedules["SRV_0083"] = 360.0
        schedules["SRV_0084"] = 405.0
        schedules["SRV_0085"] = 450.0
        schedules["SRV_0086"] = 495.0
        schedules["SRV_0087"] = 540.0
        schedules["SRV_0088"] = 585.0
        schedules["SRV_0089"] = 630.0
        schedules["SRV_0090"] = 675.0
        schedules["SRV_0091"] = 720.0
        schedules["SRV_0092"] = 765.0
        schedules["SRV_0093"] = 810.0
        schedules["SRV_0094"] = 855.0
        schedules["SRV_0095"] = 900.0
        schedules["SRV_0096"] = 945.0
        schedules["SRV_0097"] = 990.0
        schedules["SRV_0098"] = 1035.0
        schedules["SRV_0099"] = 1080.0
        schedules["SRV_0100"] = 225.0
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

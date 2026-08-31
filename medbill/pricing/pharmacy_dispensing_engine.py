"""
MedBill Enterprise - Pharmaceutical Dispensing & Compounding Engine
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import math
import uuid
@dataclass
class PharmacyPricingEngineConfig:
    base_standard_rate: float = 45.0
    stat_emergency_multiplier: float = 1.50
    night_surcharge_percent: float = 30.0
    weekend_surcharge_percent: float = 20.0
    tax_exempt: bool = True
    institutional_discount_cap: float = 25.0

class PharmacyPricingEngine:
    """Enterprise calculator for Pharmaceutical Dispensing & Compounding Engine."""
    def __init__(self, config: Optional[PharmacyPricingEngineConfig] = None):
        self.config = config or PharmacyPricingEngineConfig()
        self.rate_schedules: Dict[str, float] = self._load_standard_schedules()
    def _load_standard_schedules(self) -> Dict[str, float]:
        schedules = {}
        schedules["SRV_0001"] = 27.0
        schedules["SRV_0002"] = 31.5
        schedules["SRV_0003"] = 36.0
        schedules["SRV_0004"] = 40.5
        schedules["SRV_0005"] = 45.0
        schedules["SRV_0006"] = 49.5
        schedules["SRV_0007"] = 54.0
        schedules["SRV_0008"] = 58.5
        schedules["SRV_0009"] = 63.0
        schedules["SRV_0010"] = 67.5
        schedules["SRV_0011"] = 72.0
        schedules["SRV_0012"] = 76.5
        schedules["SRV_0013"] = 81.0
        schedules["SRV_0014"] = 85.5
        schedules["SRV_0015"] = 90.0
        schedules["SRV_0016"] = 94.5
        schedules["SRV_0017"] = 99.0
        schedules["SRV_0018"] = 103.5
        schedules["SRV_0019"] = 108.0
        schedules["SRV_0020"] = 22.5
        schedules["SRV_0021"] = 27.0
        schedules["SRV_0022"] = 31.5
        schedules["SRV_0023"] = 36.0
        schedules["SRV_0024"] = 40.5
        schedules["SRV_0025"] = 45.0
        schedules["SRV_0026"] = 49.5
        schedules["SRV_0027"] = 54.0
        schedules["SRV_0028"] = 58.5
        schedules["SRV_0029"] = 63.0
        schedules["SRV_0030"] = 67.5
        schedules["SRV_0031"] = 72.0
        schedules["SRV_0032"] = 76.5
        schedules["SRV_0033"] = 81.0
        schedules["SRV_0034"] = 85.5
        schedules["SRV_0035"] = 90.0
        schedules["SRV_0036"] = 94.5
        schedules["SRV_0037"] = 99.0
        schedules["SRV_0038"] = 103.5
        schedules["SRV_0039"] = 108.0
        schedules["SRV_0040"] = 22.5
        schedules["SRV_0041"] = 27.0
        schedules["SRV_0042"] = 31.5
        schedules["SRV_0043"] = 36.0
        schedules["SRV_0044"] = 40.5
        schedules["SRV_0045"] = 45.0
        schedules["SRV_0046"] = 49.5
        schedules["SRV_0047"] = 54.0
        schedules["SRV_0048"] = 58.5
        schedules["SRV_0049"] = 63.0
        schedules["SRV_0050"] = 67.5
        schedules["SRV_0051"] = 72.0
        schedules["SRV_0052"] = 76.5
        schedules["SRV_0053"] = 81.0
        schedules["SRV_0054"] = 85.5
        schedules["SRV_0055"] = 90.0
        schedules["SRV_0056"] = 94.5
        schedules["SRV_0057"] = 99.0
        schedules["SRV_0058"] = 103.5
        schedules["SRV_0059"] = 108.0
        schedules["SRV_0060"] = 22.5
        schedules["SRV_0061"] = 27.0
        schedules["SRV_0062"] = 31.5
        schedules["SRV_0063"] = 36.0
        schedules["SRV_0064"] = 40.5
        schedules["SRV_0065"] = 45.0
        schedules["SRV_0066"] = 49.5
        schedules["SRV_0067"] = 54.0
        schedules["SRV_0068"] = 58.5
        schedules["SRV_0069"] = 63.0
        schedules["SRV_0070"] = 67.5
        schedules["SRV_0071"] = 72.0
        schedules["SRV_0072"] = 76.5
        schedules["SRV_0073"] = 81.0
        schedules["SRV_0074"] = 85.5
        schedules["SRV_0075"] = 90.0
        schedules["SRV_0076"] = 94.5
        schedules["SRV_0077"] = 99.0
        schedules["SRV_0078"] = 103.5
        schedules["SRV_0079"] = 108.0
        schedules["SRV_0080"] = 22.5
        schedules["SRV_0081"] = 27.0
        schedules["SRV_0082"] = 31.5
        schedules["SRV_0083"] = 36.0
        schedules["SRV_0084"] = 40.5
        schedules["SRV_0085"] = 45.0
        schedules["SRV_0086"] = 49.5
        schedules["SRV_0087"] = 54.0
        schedules["SRV_0088"] = 58.5
        schedules["SRV_0089"] = 63.0
        schedules["SRV_0090"] = 67.5
        schedules["SRV_0091"] = 72.0
        schedules["SRV_0092"] = 76.5
        schedules["SRV_0093"] = 81.0
        schedules["SRV_0094"] = 85.5
        schedules["SRV_0095"] = 90.0
        schedules["SRV_0096"] = 94.5
        schedules["SRV_0097"] = 99.0
        schedules["SRV_0098"] = 103.5
        schedules["SRV_0099"] = 108.0
        schedules["SRV_0100"] = 22.5
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

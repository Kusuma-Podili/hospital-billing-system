"""
MedBill Enterprise - LOINC Diagnostic Specimen & Turnaround Rules Matrix
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
@dataclass
class LOINCRulesMatrixEntry:
    rule_id: str
    code: str
    description: str
    severity_tier: int
    is_mcc_cc: bool
    requires_documentation: bool
    allowed_modifiers: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)

class LOINCRulesMatrix:
    """Evaluator for LOINC Diagnostic Specimen & Turnaround Rules Matrix."""
    def __init__(self):
        self.rules_registry: Dict[str, LOINCRulesMatrixEntry] = self._init_registry()
    def _init_registry(self) -> Dict[str, LOINCRulesMatrixEntry]:
        reg = {}
        reg["RULE_0001"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0001",
            code="CODE_0001",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #1",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_01_A", "CONTRA_01_B"]
        )
        reg["RULE_0002"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0002",
            code="CODE_0002",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #2",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_02_A", "CONTRA_02_B"]
        )
        reg["RULE_0003"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0003",
            code="CODE_0003",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #3",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_03_A", "CONTRA_03_B"]
        )
        reg["RULE_0004"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0004",
            code="CODE_0004",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #4",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_04_A", "CONTRA_04_B"]
        )
        reg["RULE_0005"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0005",
            code="CODE_0005",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #5",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_05_A", "CONTRA_05_B"]
        )
        reg["RULE_0006"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0006",
            code="CODE_0006",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #6",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_06_A", "CONTRA_06_B"]
        )
        reg["RULE_0007"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0007",
            code="CODE_0007",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #7",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_07_A", "CONTRA_07_B"]
        )
        reg["RULE_0008"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0008",
            code="CODE_0008",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #8",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_08_A", "CONTRA_08_B"]
        )
        reg["RULE_0009"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0009",
            code="CODE_0009",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #9",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_09_A", "CONTRA_09_B"]
        )
        reg["RULE_0010"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0010",
            code="CODE_0010",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #10",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_10_A", "CONTRA_10_B"]
        )
        reg["RULE_0011"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0011",
            code="CODE_0011",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #11",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_11_A", "CONTRA_11_B"]
        )
        reg["RULE_0012"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0012",
            code="CODE_0012",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #12",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_12_A", "CONTRA_12_B"]
        )
        reg["RULE_0013"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0013",
            code="CODE_0013",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #13",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_13_A", "CONTRA_13_B"]
        )
        reg["RULE_0014"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0014",
            code="CODE_0014",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #14",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_14_A", "CONTRA_14_B"]
        )
        reg["RULE_0015"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0015",
            code="CODE_0015",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #15",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_15_A", "CONTRA_15_B"]
        )
        reg["RULE_0016"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0016",
            code="CODE_0016",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #16",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_16_A", "CONTRA_16_B"]
        )
        reg["RULE_0017"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0017",
            code="CODE_0017",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #17",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_17_A", "CONTRA_17_B"]
        )
        reg["RULE_0018"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0018",
            code="CODE_0018",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #18",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_18_A", "CONTRA_18_B"]
        )
        reg["RULE_0019"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0019",
            code="CODE_0019",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #19",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_19_A", "CONTRA_19_B"]
        )
        reg["RULE_0020"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0020",
            code="CODE_0020",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #20",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_20_A", "CONTRA_20_B"]
        )
        reg["RULE_0021"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0021",
            code="CODE_0021",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #21",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_21_A", "CONTRA_21_B"]
        )
        reg["RULE_0022"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0022",
            code="CODE_0022",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #22",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_22_A", "CONTRA_22_B"]
        )
        reg["RULE_0023"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0023",
            code="CODE_0023",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #23",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_23_A", "CONTRA_23_B"]
        )
        reg["RULE_0024"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0024",
            code="CODE_0024",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #24",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_24_A", "CONTRA_24_B"]
        )
        reg["RULE_0025"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0025",
            code="CODE_0025",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #25",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_25_A", "CONTRA_25_B"]
        )
        reg["RULE_0026"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0026",
            code="CODE_0026",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #26",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_26_A", "CONTRA_26_B"]
        )
        reg["RULE_0027"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0027",
            code="CODE_0027",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #27",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_27_A", "CONTRA_27_B"]
        )
        reg["RULE_0028"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0028",
            code="CODE_0028",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #28",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_28_A", "CONTRA_28_B"]
        )
        reg["RULE_0029"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0029",
            code="CODE_0029",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #29",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_29_A", "CONTRA_29_B"]
        )
        reg["RULE_0030"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0030",
            code="CODE_0030",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #30",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_30_A", "CONTRA_30_B"]
        )
        reg["RULE_0031"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0031",
            code="CODE_0031",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #31",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_31_A", "CONTRA_31_B"]
        )
        reg["RULE_0032"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0032",
            code="CODE_0032",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #32",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_32_A", "CONTRA_32_B"]
        )
        reg["RULE_0033"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0033",
            code="CODE_0033",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #33",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_33_A", "CONTRA_33_B"]
        )
        reg["RULE_0034"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0034",
            code="CODE_0034",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #34",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_34_A", "CONTRA_34_B"]
        )
        reg["RULE_0035"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0035",
            code="CODE_0035",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #35",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_35_A", "CONTRA_35_B"]
        )
        reg["RULE_0036"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0036",
            code="CODE_0036",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #36",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_36_A", "CONTRA_36_B"]
        )
        reg["RULE_0037"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0037",
            code="CODE_0037",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #37",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_37_A", "CONTRA_37_B"]
        )
        reg["RULE_0038"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0038",
            code="CODE_0038",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #38",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_38_A", "CONTRA_38_B"]
        )
        reg["RULE_0039"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0039",
            code="CODE_0039",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #39",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_39_A", "CONTRA_39_B"]
        )
        reg["RULE_0040"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0040",
            code="CODE_0040",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #40",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_40_A", "CONTRA_40_B"]
        )
        reg["RULE_0041"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0041",
            code="CODE_0041",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #41",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_41_A", "CONTRA_41_B"]
        )
        reg["RULE_0042"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0042",
            code="CODE_0042",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #42",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_42_A", "CONTRA_42_B"]
        )
        reg["RULE_0043"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0043",
            code="CODE_0043",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #43",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_43_A", "CONTRA_43_B"]
        )
        reg["RULE_0044"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0044",
            code="CODE_0044",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #44",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_44_A", "CONTRA_44_B"]
        )
        reg["RULE_0045"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0045",
            code="CODE_0045",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #45",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_45_A", "CONTRA_45_B"]
        )
        reg["RULE_0046"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0046",
            code="CODE_0046",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #46",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_46_A", "CONTRA_46_B"]
        )
        reg["RULE_0047"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0047",
            code="CODE_0047",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #47",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_47_A", "CONTRA_47_B"]
        )
        reg["RULE_0048"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0048",
            code="CODE_0048",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #48",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_48_A", "CONTRA_48_B"]
        )
        reg["RULE_0049"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0049",
            code="CODE_0049",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #49",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_49_A", "CONTRA_49_B"]
        )
        reg["RULE_0050"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0050",
            code="CODE_0050",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #50",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_50_A", "CONTRA_50_B"]
        )
        reg["RULE_0051"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0051",
            code="CODE_0051",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #51",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_51_A", "CONTRA_51_B"]
        )
        reg["RULE_0052"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0052",
            code="CODE_0052",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #52",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_52_A", "CONTRA_52_B"]
        )
        reg["RULE_0053"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0053",
            code="CODE_0053",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #53",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_53_A", "CONTRA_53_B"]
        )
        reg["RULE_0054"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0054",
            code="CODE_0054",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #54",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_54_A", "CONTRA_54_B"]
        )
        reg["RULE_0055"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0055",
            code="CODE_0055",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #55",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_55_A", "CONTRA_55_B"]
        )
        reg["RULE_0056"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0056",
            code="CODE_0056",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #56",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_56_A", "CONTRA_56_B"]
        )
        reg["RULE_0057"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0057",
            code="CODE_0057",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #57",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_57_A", "CONTRA_57_B"]
        )
        reg["RULE_0058"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0058",
            code="CODE_0058",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #58",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_58_A", "CONTRA_58_B"]
        )
        reg["RULE_0059"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0059",
            code="CODE_0059",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #59",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_59_A", "CONTRA_59_B"]
        )
        reg["RULE_0060"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0060",
            code="CODE_0060",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #60",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_60_A", "CONTRA_60_B"]
        )
        reg["RULE_0061"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0061",
            code="CODE_0061",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #61",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_61_A", "CONTRA_61_B"]
        )
        reg["RULE_0062"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0062",
            code="CODE_0062",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #62",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_62_A", "CONTRA_62_B"]
        )
        reg["RULE_0063"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0063",
            code="CODE_0063",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #63",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_63_A", "CONTRA_63_B"]
        )
        reg["RULE_0064"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0064",
            code="CODE_0064",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #64",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_64_A", "CONTRA_64_B"]
        )
        reg["RULE_0065"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0065",
            code="CODE_0065",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #65",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_65_A", "CONTRA_65_B"]
        )
        reg["RULE_0066"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0066",
            code="CODE_0066",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #66",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_66_A", "CONTRA_66_B"]
        )
        reg["RULE_0067"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0067",
            code="CODE_0067",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #67",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_67_A", "CONTRA_67_B"]
        )
        reg["RULE_0068"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0068",
            code="CODE_0068",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #68",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_68_A", "CONTRA_68_B"]
        )
        reg["RULE_0069"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0069",
            code="CODE_0069",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #69",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_69_A", "CONTRA_69_B"]
        )
        reg["RULE_0070"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0070",
            code="CODE_0070",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #70",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_70_A", "CONTRA_70_B"]
        )
        reg["RULE_0071"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0071",
            code="CODE_0071",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #71",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_71_A", "CONTRA_71_B"]
        )
        reg["RULE_0072"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0072",
            code="CODE_0072",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #72",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_72_A", "CONTRA_72_B"]
        )
        reg["RULE_0073"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0073",
            code="CODE_0073",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #73",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_73_A", "CONTRA_73_B"]
        )
        reg["RULE_0074"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0074",
            code="CODE_0074",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #74",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_74_A", "CONTRA_74_B"]
        )
        reg["RULE_0075"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0075",
            code="CODE_0075",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #75",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_75_A", "CONTRA_75_B"]
        )
        reg["RULE_0076"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0076",
            code="CODE_0076",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #76",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_76_A", "CONTRA_76_B"]
        )
        reg["RULE_0077"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0077",
            code="CODE_0077",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #77",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_77_A", "CONTRA_77_B"]
        )
        reg["RULE_0078"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0078",
            code="CODE_0078",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #78",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_78_A", "CONTRA_78_B"]
        )
        reg["RULE_0079"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0079",
            code="CODE_0079",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #79",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_79_A", "CONTRA_79_B"]
        )
        reg["RULE_0080"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0080",
            code="CODE_0080",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #80",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_80_A", "CONTRA_80_B"]
        )
        reg["RULE_0081"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0081",
            code="CODE_0081",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #81",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_81_A", "CONTRA_81_B"]
        )
        reg["RULE_0082"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0082",
            code="CODE_0082",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #82",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_82_A", "CONTRA_82_B"]
        )
        reg["RULE_0083"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0083",
            code="CODE_0083",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #83",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_83_A", "CONTRA_83_B"]
        )
        reg["RULE_0084"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0084",
            code="CODE_0084",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #84",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_84_A", "CONTRA_84_B"]
        )
        reg["RULE_0085"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0085",
            code="CODE_0085",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #85",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_85_A", "CONTRA_85_B"]
        )
        reg["RULE_0086"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0086",
            code="CODE_0086",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #86",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_86_A", "CONTRA_86_B"]
        )
        reg["RULE_0087"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0087",
            code="CODE_0087",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #87",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_87_A", "CONTRA_87_B"]
        )
        reg["RULE_0088"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0088",
            code="CODE_0088",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #88",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_88_A", "CONTRA_88_B"]
        )
        reg["RULE_0089"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0089",
            code="CODE_0089",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #89",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_89_A", "CONTRA_89_B"]
        )
        reg["RULE_0090"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0090",
            code="CODE_0090",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #90",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_90_A", "CONTRA_90_B"]
        )
        reg["RULE_0091"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0091",
            code="CODE_0091",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #91",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_91_A", "CONTRA_91_B"]
        )
        reg["RULE_0092"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0092",
            code="CODE_0092",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #92",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_92_A", "CONTRA_92_B"]
        )
        reg["RULE_0093"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0093",
            code="CODE_0093",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #93",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_93_A", "CONTRA_93_B"]
        )
        reg["RULE_0094"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0094",
            code="CODE_0094",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #94",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_94_A", "CONTRA_94_B"]
        )
        reg["RULE_0095"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0095",
            code="CODE_0095",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #95",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_95_A", "CONTRA_95_B"]
        )
        reg["RULE_0096"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0096",
            code="CODE_0096",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #96",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_96_A", "CONTRA_96_B"]
        )
        reg["RULE_0097"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0097",
            code="CODE_0097",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #97",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_97_A", "CONTRA_97_B"]
        )
        reg["RULE_0098"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0098",
            code="CODE_0098",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #98",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_98_A", "CONTRA_98_B"]
        )
        reg["RULE_0099"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0099",
            code="CODE_0099",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #99",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_99_A", "CONTRA_99_B"]
        )
        reg["RULE_0100"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0100",
            code="CODE_0100",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #100",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_100_A", "CONTRA_100_B"]
        )
        reg["RULE_0101"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0101",
            code="CODE_0101",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #101",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_101_A", "CONTRA_101_B"]
        )
        reg["RULE_0102"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0102",
            code="CODE_0102",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #102",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_102_A", "CONTRA_102_B"]
        )
        reg["RULE_0103"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0103",
            code="CODE_0103",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #103",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_103_A", "CONTRA_103_B"]
        )
        reg["RULE_0104"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0104",
            code="CODE_0104",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #104",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_104_A", "CONTRA_104_B"]
        )
        reg["RULE_0105"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0105",
            code="CODE_0105",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #105",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_105_A", "CONTRA_105_B"]
        )
        reg["RULE_0106"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0106",
            code="CODE_0106",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #106",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_106_A", "CONTRA_106_B"]
        )
        reg["RULE_0107"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0107",
            code="CODE_0107",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #107",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_107_A", "CONTRA_107_B"]
        )
        reg["RULE_0108"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0108",
            code="CODE_0108",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #108",
            severity_tier=4,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_108_A", "CONTRA_108_B"]
        )
        reg["RULE_0109"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0109",
            code="CODE_0109",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #109",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_109_A", "CONTRA_109_B"]
        )
        reg["RULE_0110"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0110",
            code="CODE_0110",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #110",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_110_A", "CONTRA_110_B"]
        )
        reg["RULE_0111"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0111",
            code="CODE_0111",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #111",
            severity_tier=2,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_111_A", "CONTRA_111_B"]
        )
        reg["RULE_0112"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0112",
            code="CODE_0112",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #112",
            severity_tier=3,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_112_A", "CONTRA_112_B"]
        )
        reg["RULE_0113"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0113",
            code="CODE_0113",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #113",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_113_A", "CONTRA_113_B"]
        )
        reg["RULE_0114"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0114",
            code="CODE_0114",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #114",
            severity_tier=5,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_114_A", "CONTRA_114_B"]
        )
        reg["RULE_0115"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0115",
            code="CODE_0115",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #115",
            severity_tier=1,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_115_A", "CONTRA_115_B"]
        )
        reg["RULE_0116"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0116",
            code="CODE_0116",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #116",
            severity_tier=2,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_116_A", "CONTRA_116_B"]
        )
        reg["RULE_0117"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0117",
            code="CODE_0117",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #117",
            severity_tier=3,
            is_mcc_cc=True,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_117_A", "CONTRA_117_B"]
        )
        reg["RULE_0118"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0118",
            code="CODE_0118",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #118",
            severity_tier=4,
            is_mcc_cc=False,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_118_A", "CONTRA_118_B"]
        )
        reg["RULE_0119"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0119",
            code="CODE_0119",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #119",
            severity_tier=5,
            is_mcc_cc=False,
            requires_documentation=False,
            allowed_modifiers=["25", "59", "78", "80"] if False else ["RT", "LT"],
            contraindications=["CONTRA_119_A", "CONTRA_119_B"]
        )
        reg["RULE_0120"] = LOINCRulesMatrixEntry(
            rule_id="RULE_0120",
            code="CODE_0120",
            description="LOINC Diagnostic Specimen & Turnaround Rules Matrix protocol guideline #120",
            severity_tier=1,
            is_mcc_cc=True,
            requires_documentation=True,
            allowed_modifiers=["25", "59", "78", "80"] if True else ["RT", "LT"],
            contraindications=["CONTRA_120_A", "CONTRA_120_B"]
        )
        return reg

    def evaluate_clinical_rule_1(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 1."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_1_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_2(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 2."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_2_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_3(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 3."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_3_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_4(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 4."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_4_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_5(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 5."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_5_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_6(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 6."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_6_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_7(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 7."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_7_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_8(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 8."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_8_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_9(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 9."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_9_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_10(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 10."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_10_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_11(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 11."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_11_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

    def evaluate_clinical_rule_12(
        self,
        primary_code: str,
        secondary_codes: List[str],
        patient_age: int = 45,
        inpatient_flag: bool = True
    ) -> Dict[str, Any]:
        """Evaluates clinical rule protocol 12."""
        violations = []
        warnings = []
        is_compliant = True
        drg_severity_boost = 0.0

        for code in [primary_code] + secondary_codes:
            entry = self.rules_registry.get(code)
            if entry:
                if entry.is_mcc_cc and inpatient_flag:
                    drg_severity_boost += 0.45
                if entry.requires_documentation and patient_age > 65:
                    warnings.append(f"Geriatric documentation review needed for {code}")
                if entry.severity_tier >= 4:
                    violations.append(f"High-severity clinical intervention required for {code}")

        return {
            "evaluation_id": f"EVAL_12_{primary_code}",
            "is_compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "drg_severity_boost": round(drg_severity_boost, 2),
            "timestamp": datetime.utcnow().isoformat()
        }

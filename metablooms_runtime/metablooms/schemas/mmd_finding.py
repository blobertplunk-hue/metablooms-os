"""Missing Middle Detector schema.

MMD emits findings describing missing links between:
- plan <-> code
- code <-> evidence
- evidence <-> gate
- loop <-> convergence

Fail-closed principle:
- Any BLOCK finding prevents ship/publish actions once wired.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, Optional


class MMDAxis(str, Enum):
    PLAN_CODE = "PLAN_CODE"
    CODE_EVIDENCE = "CODE_EVIDENCE"
    EVIDENCE_GATE = "EVIDENCE_GATE"
    LOOP_CONVERGENCE = "LOOP_CONVERGENCE"


class MMDSeverity(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    BLOCK = "BLOCK"


@dataclass
class MMDFinding:
    finding_id: str
    axis: MMDAxis
    severity: MMDSeverity
    missing_link: str

    # Optional fields
    responsible_segment: Optional[str] = None
    remediation_hint: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.finding_id:
            raise ValueError("finding_id is required")
        if not self.missing_link:
            raise ValueError("missing_link is required")

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["axis"] = self.axis.value
        d["severity"] = self.severity.value
        return d

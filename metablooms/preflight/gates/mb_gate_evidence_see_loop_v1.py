"""MetaBlooms Gate: GATE.EVIDENCE.SEE.LOOP.V1

ECL_VERSION: 1
ECL_SCOPE: PREFLIGHT.GATES
ECL_RESPONSIBILITY: Enforce CODE.AUTHORSHIP.REQUIRES.SEE.LOOP invariant via Missing Middle Detector.

Fail-closed behavior:
- If the missing-middle detector emits any BLOCK finding, this gate fails.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from metablooms.validators.missing_middle_detector_v1 import detect_missing_middle

GATE_ID = "GATE.EVIDENCE.SEE.LOOP.V1"
P0 = True


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = context.get("root") or context.get("os_root") or context.get("zroot") or "."
    findings = detect_missing_middle(str(root))

    block = [f for f in findings if f.get("severity") == "BLOCK"]
    ok = len(block) == 0

    out: Dict[str, Any] = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": ok,
        "errors": block if not ok else [],
        "warnings": [f for f in findings if f.get("severity") == "WARN"],
        "evidence": {"root": str(root), "findings_total": len(findings)},
    }

    if ledger_writer is not None:
        ledger_writer({"event_type": "GATE_RESULT", **out})
    return out

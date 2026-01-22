"""P0-DCC Acceptance Runner v1

This runner validates that:
- gate file exists
- recursive controller exists
- gate contains required enforcement clauses (SEE + recursion + telemetry)
It is a static verification helper (no execution of the system under test).
"""

from __future__ import annotations

from pathlib import Path

REQUIRED_SNIPPETS = [
    "SEE required but missing artifacts",
    "telemetry required but missing artifacts",
    "C2+ work requires recursive loop controller evidence",
    "MB_P0_DEBUG_GOVERNANCE_V1"
]

def run_acceptance(repo_root: str) -> dict:
    root = Path(repo_root)
    gate = root / "metablooms" / "governance" / "p0_dcc_v1" / "mb_p0_debug_gate.py"
    loop = root / "metablooms" / "governance" / "p0_dcc_v1" / "see_recursive_controller_v1.py"

    result = {
        "gate_exists": gate.exists(),
        "loop_controller_exists": loop.exists(),
        "snippets_present": {},
        "all_passed": False
    }

    if not gate.exists() or not loop.exists():
        result["all_passed"] = False
        return result

    txt = gate.read_text(errors="ignore")
    for s in REQUIRED_SNIPPETS:
        result["snippets_present"][s] = (s in txt)

    result["all_passed"] = result["gate_exists"] and result["loop_controller_exists"] and all(result["snippets_present"].values())
    return result

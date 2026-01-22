# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# ECL:
#   id: MB_GATE_EXCODE_ECL_V1
#   role: gate
#   owns: [invoke_excode_ecl_validator]
#   does_not: [execute_user_code, mutate_repo]
#   inputs: [run_context:dict]
#   outputs: [gate_result:dict]
#   side_effects: [none]
#   failure_modes: [VALIDATION_FAILED]
#   invariants: [LEAF_GATE_PURITY]
#   evidence: [returned gate_result dict]
#   last_reviewed: 2026-01-16
"""Preflight Leaf Gate: Extraordinary Coding Clarity Layer (v1)

Intent
Return structured EXCODE_ECL_V1 compliance results for orchestrators to record in the ledger.

Scope
- Runs EXCODE_ECL validator across repository root specified in run_context.

Non-Goals
- No ledger writes (orchestrator owns those).
- No repo mutation.

Inputs
run_context (dict): must include repo_root; may include excode_ecl_mode ('WARN'|'FAIL').

Outputs
dict: {gate_id, pass, violations[], scope}

Side Effects
None.

Failure Modes
VALIDATION_FAILED when validator returns pass=False in FAIL mode.

Invariants
Leaf gate purity: returns data only.

Evidence & Observability
Orchestrator ledger event for this gate is the authoritative evidence.

Examples
result = gate_excode_ecl_v1({"repo_root": ".", "excode_ecl_mode": "WARN"})

Maintenance Notes
Raise enforcement after coverage threshold is met.
"""

from __future__ import annotations
from typing import Any, Dict

from metablooms.validators.excode_ecl_validate_v1 import validate_repo

GATE_ID = "GATE.EXCODE.ECL.V1"

def gate_excode_ecl_v1(run_context: Dict[str, Any]) -> Dict[str, Any]:
    repo_root = run_context.get("repo_root", ".")
    mode = run_context.get("excode_ecl_mode", "WARN")
    result = validate_repo(repo_root, mode=mode)
    return {
        "gate_id": GATE_ID,
        "pass": bool(result.get("pass")),
        "violations": result.get("violations", []),
        "scope": {"repo_root": repo_root, "mode": mode, "coverage": result.get("coverage", {})},
    }

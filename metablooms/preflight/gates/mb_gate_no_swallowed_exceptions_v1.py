# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# ECL:
#   id: MB_GATE_NO_SWALLOWED_EXCEPTIONS_V1
#   role: gate
#   owns: [invoke_no_swallowed_exceptions_validator]
#   does_not: [execute_user_code, mutate_repo]
#   inputs: [run_context:dict]
#   outputs: [gate_result:dict]
#   side_effects: [none]
#   failure_modes: [VALIDATION_FAILED]
#   invariants: [LEAF_GATE_PURITY]
#   evidence: [returned gate_result dict]
#   last_reviewed: 2026-01-16

from __future__ import annotations

from typing import Any, Dict

from metablooms.validators.mb_validate_no_swallowed_exceptions_v1 import validate_repo

GATE_ID = "GATE.CODE.NO_SWALLOWED_EXCEPTIONS.V1"


def run_gate(run_context: Dict[str, Any]) -> Dict[str, Any]:
    repo_root = run_context.get("repo_root", ".")
    mode = run_context.get("mb_no_swallowed_exceptions_mode", "WARN")
    result = validate_repo(repo_root, mode=mode)
    return {
        "gate_id": GATE_ID,
        "pass": bool(result.get("pass")),
        "violations": result.get("violations", []),
        "scope": {"repo_root": repo_root, "mode": mode, "scanned": result.get("scanned", {})},
    }

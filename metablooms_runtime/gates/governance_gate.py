from __future__ import annotations

from typing import Any, Dict

from metablooms.loop.see_recursive_controller import SEEStopReason
from metablooms.mmd.mmd_axes import run_mmd
from metablooms.ecl.ecl_gate import run_ecl_checks


class GovernanceBlock(Exception):
    """Raised when governance MUST halt execution."""


def _normalize_mmd_inputs(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Accepts flexible/legacy keys and normalizes to run_mmd signature."""
    # Required keys
    plan = raw.get('plan')
    code_refs = raw.get('code_refs') or []
    evidence_pointers = raw.get('evidence_pointers') or []
    gate_passed = bool(raw.get('gate_passed', False))

    # Normalize iteration fields
    if 'iteration' in raw:
        iteration = int(raw.get('iteration') or 0)
    else:
        iteration = int(raw.get('iterations') or 0)

    if 'max_iterations' in raw:
        max_iterations = int(raw.get('max_iterations') or 0)
    else:
        max_iterations = int(raw.get('max') or raw.get('max_iters') or raw.get('max_iterations') or 0)
        if max_iterations == 0:
            # default to iteration if unknown
            max_iterations = max(iteration, 1)

    if 'improved' in raw:
        improved = bool(raw.get('improved'))
    else:
        improved = bool(raw.get('improvement'))

    return {
        'plan': plan,
        'code_refs': code_refs,
        'evidence_pointers': evidence_pointers,
        'gate_passed': gate_passed,
        'iteration': iteration,
        'max_iterations': max_iterations,
        'improved': improved,
    }


def run_governance_gate(*, see_stop_reason: Any, mmd_inputs: Dict[str, Any], ecl_inputs: Dict[str, Any]) -> None:
    """Raise GovernanceBlock on any violation; return None on success."""
    if see_stop_reason != SEEStopReason.SUCCESS:
        raise GovernanceBlock(f"SEE not SUCCESS: {see_stop_reason}")

    mmd_norm = _normalize_mmd_inputs(mmd_inputs)
    if run_mmd(**mmd_norm).has_blockers:
        raise GovernanceBlock('MMD BLOCK')

    if run_ecl_checks(**ecl_inputs).has_blockers:
        raise GovernanceBlock('ECL BLOCK')

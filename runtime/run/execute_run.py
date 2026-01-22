# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""runtime/run/execute_run.py

Canonical run lifecycle entry for governed execution.

This module exists to provide a **single, real call site** for:
- Preflight Orchestrator v1

It is intentionally minimal and deterministic.
"""

from __future__ import annotations

from typing import Any, Dict

from metablooms.preflight.preflight_orchestrator_v1 import run_preflight
from metablooms.postrun.postrun_hook_v1 import run_postrun_review


def execute_run(run_context: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a governed run.

    Current v1 behavior:
    - Run preflight and fail-closed on any P0 failure.
    - Return the preflight summary (execution planner not yet wired).
    """

    pf = run_preflight(run_context)

    # Post-run review is always invoked after preflight completes (pass or fail).
    # PRR must not mutate state beyond writing review artifacts.
    run_postrun_review(run_context=run_context, preflight_result=pf)

    if not pf.get("ok"):
        # Fail-closed: caller must not publish or mutate state after this.
        return pf

    # Placeholder: execution stage is out of scope for this delta.
    return pf

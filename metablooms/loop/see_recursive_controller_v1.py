from typing import Any, Callable, Dict, Optional

from metablooms.evidence.receipt_validate_v1 import validate_receipt
from metablooms.evidence.regression_signature_v1 import RegressionTracker


class LoopAbort(Exception):
    pass


def run_see_loop(
    task_spec: Dict[str, Any],
    executor: Callable[[Dict[str, Any], int], Dict[str, Any]],
    diagnoser: Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]],
    patch_provider: Callable[[Dict[str, Any]], Optional[Dict[str, Any]]],
    patch_applier: Callable[[Dict[str, Any]], None],
    *,
    max_iterations: int = 3,
    ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None,
    required_evidence_level: str = "E3",
    require_stable_passes: int = 1,
) -> Dict[str, Any]:
    """Bounded, deterministic SEE loop.

    The controller itself does not execute shell or edit files. It only:
      - calls executor
      - validates receipts
      - checks stop conditions
      - calls diagnoser
      - obtains a patch spec from patch_provider
      - applies patch via patch_applier

    Stop conditions are fail-closed.
    """
    if max_iterations < 1:
        raise ValueError("max_iterations must be >= 1")

    artifact_id = str(task_spec.get("artifact_id") or task_spec.get("task_id") or "").strip() or "UNKNOWN"

    evidence_order = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4}
    if required_evidence_level not in evidence_order:
        raise ValueError("invalid required_evidence_level")

    baseline_path = str(task_spec.get("regression_baseline_path") or "")
    tracked = task_spec.get("regression_paths") or []
    tracker = RegressionTracker(baseline_path, tracked_paths=list(tracked)) if baseline_path else None

    stable_passes = 0
    last_result: Optional[Dict[str, Any]] = None

    for i in range(1, max_iterations + 1):
        result = executor(task_spec, i)
        last_result = result

        receipt_path = result.get("receipt_path")
        if not isinstance(receipt_path, str) or not receipt_path:
            raise LoopAbort("MISSING_RECEIPT_PATH")

        validate_receipt(receipt_path)

        if ledger_writer is not None:
            ledger_writer({
                "event_type": "SEE_LOOP_ITERATION",
                "artifact_id": artifact_id,
                "iteration": i,
                "receipt_path": receipt_path,
            })

        exit_code = int(result.get("exit_code") or 1)
        evidence_claimed = str(result.get("evidence_level_claimed") or "E1")

        # Pass condition: exit_code==0 AND evidence >= required AND regression passes.
        pass_basic = exit_code == 0 and evidence_order.get(evidence_claimed, -1) >= evidence_order[required_evidence_level]

        if pass_basic:
            if tracker is not None:
                reg = tracker.check()
                if reg.reason == "NO_BASELINE":
                    tracker.capture_baseline()
                    reg = tracker.check()
                if not reg.ok:
                    stable_passes = 0
                else:
                    stable_passes += 1
            else:
                stable_passes += 1

            if stable_passes >= require_stable_passes:
                return {
                    "status": "PASS",
                    "final_iteration": i,
                    "final_receipt_path": receipt_path,
                    "stable_passes": stable_passes,
                }
        else:
            stable_passes = 0

        diagnosis = diagnoser(task_spec, result)
        patch = patch_provider(diagnosis)
        if not patch:
            return {
                "status": "FAIL",
                "final_iteration": i,
                "final_receipt_path": receipt_path,
                "failure_reason": "NO_PATCH_AVAILABLE",
                "diagnosis": diagnosis,
            }

        patch_applier(patch)

    # exceeded bound
    return {
        "status": "FAIL",
        "final_iteration": max_iterations,
        "final_receipt_path": (last_result or {}).get("receipt_path"),
        "failure_reason": "MAX_ITERATIONS_EXCEEDED",
    }

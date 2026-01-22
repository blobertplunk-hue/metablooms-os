"""SEE (Sandcrawler Evidence Engine) recursive loop controller.

Phase: 2 (iteration accounting)

ECL (Extraordinary Coding Law) headers:
ECL_VERSION: 1
ECL_SCOPE: metablooms.loop.see_recursive_controller
ECL_RESPONSIBILITY: Deterministic bounded recursion + receipt emission. No network IO. Evidence-first.

This controller does not implement crawling. It orchestrates:
- iterative execution steps (provided as callables)
- receipt creation for each iteration
- stop reason selection

Downstream gates (Phase 5+) should fail-closed if receipts are missing or invalid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from metablooms.schemas.see_receipt import SEEIterationReceipt, SEELoopReceipt, SEEStopReason
from metablooms.loop.see_receipts_store import (
    init_loop_run,
    write_iteration_receipt,
    write_loop_receipt,
    write_manifest,
    utc_now_iso,
)


@dataclass(frozen=True)
class SEELoopConfig:
    task_id: str
    max_iterations: int = 5
    output_root: str = "."


# Types
StepFn = Callable[[int, Dict[str, Any]], Dict[str, Any]]
MMDRunFn = Callable[[Dict[str, Any]], Dict[str, Any]]
ECLCheckFn = Callable[[Dict[str, Any]], Dict[str, Any]]
SuccessFn = Callable[[Dict[str, Any]], bool]


def run_see_loop(
    cfg: SEELoopConfig,
    step_fn: StepFn,
    success_fn: Optional[SuccessFn] = None,
    mmd_fn: Optional[MMDRunFn] = None,
    ecl_fn: Optional[ECLCheckFn] = None,
    initial_inputs: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """Run a bounded SEE loop.

    Returns:
      (loop_dir, stop_reason)

    Fail-closed behavior:
    - If cfg is invalid, returns INVALID_INPUT and writes a loop receipt.
    - If step_fn raises, returns EXECUTION_ERROR and records error in receipt.

    NOTE: MMD/ECL hooks are called if provided; otherwise they default to passing summaries.
    """

    if cfg.max_iterations <= 0:
        loop_id, loop_dir, started = init_loop_run(cfg.output_root, cfg.task_id)
        ended = utc_now_iso()
        lr = SEELoopReceipt(
            loop_id=loop_id,
            task_id=cfg.task_id,
            started_utc=started,
            ended_utc=ended,
            max_iterations=cfg.max_iterations,
            stop_reason=SEEStopReason.INVALID_INPUT.value,
            iteration_receipts=[],
            iterations_run=0,
        )
        write_loop_receipt(loop_dir, lr)
        write_manifest(loop_dir)
        return loop_dir, SEEStopReason.INVALID_INPUT.value

    loop_id, loop_dir, started = init_loop_run(cfg.output_root, cfg.task_id)
    inputs = dict(initial_inputs or {})

    iter_files: List[str] = []
    stop_reason = SEEStopReason.MAX_ITERATIONS_REACHED.value

    for i in range(1, cfg.max_iterations + 1):
        iter_started = utc_now_iso()
        error: Optional[str] = None

        # Execute step
        try:
            outputs = step_fn(i, inputs)
        except Exception as e:  # noqa: BLE001 (intentional capture; fail-closed)
            outputs = {}
            error = f"STEP_ERROR: {type(e).__name__}: {e}"

        # Run ECL check (summary only here)
        ecl_summary = {"pass": True, "mode": "UNSPECIFIED"}
        if ecl_fn is not None:
            try:
                ecl_summary = dict(ecl_fn({"inputs": inputs, "outputs": outputs, "iteration": i}))
            except Exception as e:  # noqa: BLE001
                ecl_summary = {"pass": False, "error": f"ECL_ERROR: {type(e).__name__}: {e}"}

        if not bool(ecl_summary.get("pass", False)):
            stop_reason = SEEStopReason.BLOCKED_BY_ECL.value

        # Run MMD (summary only here)
        mmd_summary = {"block": False, "findings": 0}
        if mmd_fn is not None:
            try:
                mmd_summary = dict(mmd_fn({"inputs": inputs, "outputs": outputs, "iteration": i}))
            except Exception as e:  # noqa: BLE001
                mmd_summary = {"block": True, "error": f"MMD_ERROR: {type(e).__name__}: {e}"}

        if bool(mmd_summary.get("block", False)):
            stop_reason = SEEStopReason.BLOCKED_BY_MMD.value

        # Determine success
        ok = False
        if success_fn is not None and stop_reason not in (
            SEEStopReason.BLOCKED_BY_ECL.value,
            SEEStopReason.BLOCKED_BY_MMD.value,
            SEEStopReason.EXECUTION_ERROR.value,
        ):
            try:
                ok = bool(success_fn({"inputs": inputs, "outputs": outputs, "iteration": i}))
            except Exception as e:  # noqa: BLE001
                ok = False
                error = (error + " | " if error else "") + f"SUCCESS_FN_ERROR: {type(e).__name__}: {e}"

        iter_ended = utc_now_iso()

        receipt = SEEIterationReceipt(
            loop_id=loop_id,
            task_id=cfg.task_id,
            iteration=i,
            started_utc=iter_started,
            ended_utc=iter_ended,
            inputs_snapshot=dict(inputs),
            outputs_snapshot=dict(outputs),
            evidence_pointers=list(outputs.get("evidence_pointers", [])) if isinstance(outputs, dict) else [],
            mmd_summary=mmd_summary,
            ecl_summary=ecl_summary,
            error=error,
        )
        iter_files.append(write_iteration_receipt(loop_dir, receipt))

        # Update inputs for next iteration (deterministic: merge outputs['next_inputs'] if provided)
        if isinstance(outputs, dict) and isinstance(outputs.get("next_inputs"), dict):
            inputs = dict(outputs["next_inputs"])  # explicit replacement to avoid drift

        # Decide stop
        if error is not None and stop_reason == SEEStopReason.MAX_ITERATIONS_REACHED.value:
            stop_reason = SEEStopReason.EXECUTION_ERROR.value

        if stop_reason in (SEEStopReason.BLOCKED_BY_ECL.value, SEEStopReason.BLOCKED_BY_MMD.value):
            break

        if ok:
            stop_reason = SEEStopReason.SUCCESS.value
            break

    ended = utc_now_iso()
    loop_receipt = SEELoopReceipt(
        loop_id=loop_id,
        task_id=cfg.task_id,
        started_utc=started,
        ended_utc=ended,
        max_iterations=cfg.max_iterations,
        stop_reason=stop_reason,
        iteration_receipts=iter_files,
        iterations_run=len(iter_files),
    )

    write_loop_receipt(loop_dir, loop_receipt)
    write_manifest(loop_dir)

    return loop_dir, stop_reason

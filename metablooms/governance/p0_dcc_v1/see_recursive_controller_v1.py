"""SEE Recursive Controller v1.1 (P0)

Required execution surface for C2+ CODE/DEBUG work.

This controller is responsible for:
- materializing loop artifacts (receipts + summary)
- appending iteration outcomes (tests, SEE status, ECL pass/fail)
- providing an explicit certification marker when ECL passes

Outputs (project-relative):
- loop/LOOP_RECEIPTS.json
- loop/LOOP_SUMMARY.md
- ecl/ECL_PASS.json   (only when certified)

Posture:
- Append-only; never delete prior evidence
- No correctness claims without ECL_PASS.json
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LoopResult:
    ok: bool
    iterations: int
    receipts_path: str
    summary_path: str
    ecl_pass_path: Optional[str]
    notes: str


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8", errors="ignore") or "{}")


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2), encoding="utf-8")


def _append_iteration(receipts: Dict[str, Any], entry: Dict[str, Any]) -> None:
    receipts.setdefault("iterations", [])
    receipts["iterations"].append(entry)


def run_loop(
    *,
    repo_root: str,
    context: Dict[str, Any],
    max_iters: int = 3,
    iteration_outcomes: Optional[List[Dict[str, Any]]] = None,
) -> LoopResult:
    """Run / record a bounded ideated recursion loop.

    This function always writes loop artifacts.
    If iteration_outcomes are provided, they are appended as evidence.
    If an outcome indicates ecl_pass=True, controller emits ecl/ECL_PASS.json.
    """

    root = Path(repo_root)
    loop_dir = root / "loop"
    ecl_dir = root / "ecl"
    loop_dir.mkdir(parents=True, exist_ok=True)
    ecl_dir.mkdir(parents=True, exist_ok=True)

    receipts_path = loop_dir / "LOOP_RECEIPTS.json"
    summary_path = loop_dir / "LOOP_SUMMARY.md"
    ecl_pass_path = ecl_dir / "ECL_PASS.json"

    receipts = _load_json(receipts_path) if receipts_path.exists() else {
        "policy": "MB_P0_DEBUG_GOVERNANCE_V1",
        "run_id": context.get("run_id", "RUN_UNKNOWN"),
        "attempt_id": context.get("attempt_id", "A1"),
        "created_utc": time.time(),
        "max_iters": max_iters,
        "iterations": []
    }

    # Add structural iterations if none exist yet
    if not receipts.get("iterations"):
        for i in range(1, max_iters + 1):
            _append_iteration(receipts, {
                "iter": i,
                "timestamp": time.time(),
                "intent": "ITERATE_UNTIL_ECL_PASS",
                "expected_artifacts": [
                    "DEBUG_HYPOTHESIS_LEDGER.json",
                    "INVARIANT_LIST.md",
                    "PROOF_BUNDLE.md"
                ],
                "outcome": None
            })

    # Append provided outcomes (append-only)
    if iteration_outcomes:
        for out in iteration_outcomes:
            _append_iteration(receipts, {
                "iter": out.get("iter", None),
                "timestamp": time.time(),
                "intent": out.get("intent", "ITERATION_OUTCOME"),
                "expected_artifacts": out.get("expected_artifacts", []),
                "outcome": {
                    "tests_passed": bool(out.get("tests_passed", False)),
                    "see_ok": bool(out.get("see_ok", False)),
                    "ecl_pass": bool(out.get("ecl_pass", False)),
                    "notes": out.get("notes", "")
                }
            })

    # Emit summary (append-only note; overwrite is acceptable for summary because it is derivative)
    summary_lines = [
        "P0 LOOP SUMMARY",
        "",
        f"run_id: {receipts.get('run_id')}",
        f"attempt_id: {receipts.get('attempt_id')}",
        f"max_iters: {receipts.get('max_iters')}",
        f"total_iteration_entries: {len(receipts.get('iterations', []))}",
        "",
        "Certification requires ecl/ECL_PASS.json and loop receipts containing an outcome with ecl_pass=true.",
        "",
    ]
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

    # Determine certification
    certified = False
    for it in receipts.get("iterations", []):
        oc = it.get("outcome") or {}
        if oc.get("ecl_pass") is True:
            certified = True
            break

    if certified:
        _write_json(ecl_pass_path, {
            "policy": "MB_P0_DEBUG_GOVERNANCE_V1",
            "run_id": receipts.get("run_id"),
            "attempt_id": receipts.get("attempt_id"),
            "certified_utc": time.time(),
            "ecl_pass": True,
            "note": "Certification marker. Claims at C2+ may be promoted only when this exists."
        })

    _write_json(receipts_path, receipts)

    return LoopResult(
        ok=certified,
        iterations=max_iters,
        receipts_path="loop/LOOP_RECEIPTS.json",
        summary_path="loop/LOOP_SUMMARY.md",
        ecl_pass_path="ecl/ECL_PASS.json" if certified else None,
        notes="Loop artifacts written. Provide iteration_outcomes to append evidence; certification requires ecl_pass outcome."
    )

"""MetaBlooms Phase 2.1 — Enforcement Hooks

Defines callable surfaces and required checks for Phase 2.1 engine routing.
This module is intentionally minimal but non-placeholder: it emits telemetry and
enforces single-engine selection semantics.

No claims of full runtime activation are made here; integration is performed by
the OS runtime pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional
import json
import time

EngineID = Literal["ELE", "ITLE", "NBE", "MBE", "TDAE", "NONE"]


@dataclass(frozen=True)
class RunContext:
    repo_root: str
    turn_id: str
    phase: str = "2.1"


def _telemetry_path(ctx: RunContext) -> Path:
    tdir = Path(ctx.repo_root) / "telemetry"
    tdir.mkdir(parents=True, exist_ok=True)
    return tdir / "phase2_1_hooks.jsonl"


def emit_telemetry(ctx: RunContext, engine: EngineID, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
    obj: Dict[str, Any] = {
        "ts": time.time(),
        "turn_id": ctx.turn_id,
        "phase": ctx.phase,
        "engine": engine,
        "event": event,
    }
    if payload:
        obj["payload"] = payload
    p = _telemetry_path(ctx)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")


def select_engine(candidates: List[EngineID]) -> EngineID:
    """Select exactly one engine based on strict priority order."""
    priority: List[EngineID] = ["ELE", "ITLE", "NBE", "MBE", "TDAE", "NONE"]
    cand_set = set(candidates)
    for e in priority:
        if e in cand_set:
            return e
    return "NONE"


def apply_mutation(selected: EngineID, ctx: RunContext) -> None:
    """Emit telemetry indicating which engine would apply mutation.

    Actual mutation is performed by engine-specific modules once integrated.
    """
    emit_telemetry(ctx, selected, "MUTATION_SELECTED", {"selected_engine": selected})


def nano_to_macro_evaluator(ctx: RunContext, nanobloom_counts: Dict[str, int], *, threshold: int = 5) -> List[str]:
    """Return nanobloom ids eligible for MacroBloom review eligibility."""
    eligible = [nb for nb, c in nanobloom_counts.items() if int(c) >= int(threshold)]
    if eligible:
        emit_telemetry(ctx, "MBE", "MACROBLOOM_REVIEW_ELIGIBLE", {"nanoblooms": eligible, "threshold": threshold})
    return eligible

#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Evolution Seam (observe-only, governance-bounded).

Per evolution_wiring_spec_v1.md:
- Sits between normalization and execution planner.
- Observes methodology/tooling signals.
- Selects variants under constraints.
- Cannot override governance, invariants, receipts schema.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

FORBIDDEN_FIELDS = {"governance_override","disable_validators","rewrite_invariants"}

@dataclass(frozen=True)
class Selection:
    variant_id: str
    reason: str
    constraints: Dict[str, Any]

def observe_methodology(signals: Dict[str, Any]) -> Dict[str, Any]:
    # Pass-through observation: normalize known keys, never mutate governance.
    obs = {
        "loop_count": int(signals.get("loop_count", 0) or 0),
        "tool_mismatch": bool(signals.get("tool_mismatch", False)),
        "error_signature": signals.get("error_signature"),
    }
    return obs

def select_variant(available_variants: List[str], fitness_state: Dict[str, Any], constraints: Dict[str, Any]) -> Selection:
    # Fail-closed constraints check
    for k in constraints.keys():
        if k in FORBIDDEN_FIELDS:
            raise RuntimeError(f"EVOLUTION_GOVERNANCE_VIOLATION: forbidden constraint field {k}")

    if not available_variants:
        return Selection(variant_id="default", reason="no variants provided", constraints={})

    # Simple bounded selection: prefer highest-scored if present
    scores = fitness_state.get("scores", {}) if isinstance(fitness_state, dict) else {}
    best = None
    best_score = None
    for vid in available_variants:
        sc = scores.get(vid)
        if sc is None:
            continue
        if best is None or sc > best_score:
            best, best_score = vid, sc
    if best is None:
        best = available_variants[0]
        return Selection(variant_id=best, reason="fallback-first-variant", constraints=constraints)
    return Selection(variant_id=best, reason="fitness-max", constraints=constraints)

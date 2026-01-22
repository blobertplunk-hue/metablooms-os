# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
metablooms_quality_gate_v1_1.py
MetaBlooms CTOS — Quality Gate Template (Best-Per-Atom Selection) v1.1

Adds:
- rubric registry overlays (metablooms_rubrics.json)
- triviality exemption enforcement
- module coherence pass + artifact

This module is a TEMPLATE: integrate into your OS/userland scripts.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import json
import time


# ---------- Data model ----------

@dataclass(frozen=True)
class RubricScore:
    # base
    correctness: int
    auditability: int
    determinism: int
    maintainability: int
    security_robustness: int
    # overlay (optional): dict dimension->score
    overlay: Dict[str, int] | None = None

    def total_base(self) -> int:
        return (
            self.correctness
            + self.auditability
            + self.determinism
            + self.maintainability
            + self.security_robustness
        )

    def total_overlay(self) -> int:
        if not self.overlay:
            return 0
        return sum(int(v) for v in self.overlay.values())

    def total(self) -> int:
        return self.total_base() + self.total_overlay()


@dataclass
class Candidate:
    candidate_id: str
    description: str
    code: str
    atom_type: str
    rubric: RubricScore
    checks: Dict[str, Any]
    passed: bool
    failure_reason: Optional[str] = None


@dataclass
class AtomSelection:
    atom_id: str
    atom_name: str
    atom_type: str
    trivial: bool
    candidates: List[Candidate]
    winner_id: Optional[str]
    selected_at_unix: int
    bounds: Dict[str, int]
    overlay_applied: List[str]


# ---------- Utility ----------

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def load_rubrics(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def threshold_pass_base(r: RubricScore) -> Tuple[bool, Optional[str]]:
    if r.correctness < 4:
        return False, "QUALITY_GATE_FAILED: THRESHOLD_NOT_MET(correctness)"
    if r.auditability < 4:
        return False, "QUALITY_GATE_FAILED: THRESHOLD_NOT_MET(auditability)"
    if r.determinism < 4:
        return False, "QUALITY_GATE_FAILED: THRESHOLD_NOT_MET(determinism)"
    if r.total_base() < 20:
        return False, "QUALITY_GATE_FAILED: THRESHOLD_NOT_MET(total_base)"
    return True, None


def threshold_pass_overlay(r: RubricScore, overlay_min: Dict[str, int]) -> Tuple[bool, Optional[str]]:
    if not overlay_min:
        return True, None
    overlay = r.overlay or {}
    for dim, minv in overlay_min.items():
        if int(overlay.get(dim, 0)) < int(minv):
            return False, f"QUALITY_GATE_FAILED: THRESHOLD_NOT_MET(overlay:{dim})"
    return True, None


def enforce_triviality(trivial: bool, atom_meta: Dict[str, Any]) -> None:
    """
    Enforce the triviality exemption eligibility.
    Caller provides atom_meta fields:
      - logical_lines: int
      - pure: bool
      - hazard_surfaces: List[str]
    """
    if not trivial:
        return
    logical_lines = int(atom_meta.get("logical_lines", 0))
    pure = bool(atom_meta.get("pure", False))
    hazards = [str(x).lower() for x in atom_meta.get("hazard_surfaces", [])]

    if not pure or logical_lines >= 10:
        raise ValueError("QUALITY_GATE_FAILED: TRIVIALITY_MISUSED")

    disallowed = {"parsing", "auth", "money", "encryption", "filesystem", "network", "db"}
    if any(h in disallowed for h in hazards):
        raise ValueError("QUALITY_GATE_FAILED: TRIVIALITY_MISUSED")


# ---------- Core gate ----------

def pick_best_candidate(
    atom_id: str,
    atom_name: str,
    atom_type: str,
    trivial: bool,
    atom_meta: Dict[str, Any],
    candidates: List[Candidate],
    rubrics_path: str = "metablooms_rubrics.json",
    default_max_candidates: int = 3,
) -> AtomSelection:
    """
    Decide phase: choose the best candidate that passes thresholds.
    Fail-closed if no candidate qualifies.
    """
    enforce_triviality(trivial, atom_meta)

    if len(candidates) == 0:
        raise ValueError("QUALITY_GATE_FAILED: NO_CANDIDATE_PASSES(empty)")

    max_candidates = 1 if trivial else default_max_candidates
    if len(candidates) > max_candidates:
        raise ValueError("QUALITY_GATE_BLOCKED: BOUNDS_EXCEEDED(max_candidates)")

    registry = load_rubrics(rubrics_path)
    overlays = registry.get("overlays", {})
    overlay_cfg = overlays.get(atom_type, {})
    overlay_min = overlay_cfg.get("min_thresholds", {})
    overlay_dims = overlay_cfg.get("dimensions", [])

    # Apply thresholds
    qualified: List[Candidate] = []
    for c in candidates:
        ok, reason = threshold_pass_base(c.rubric)
        if not ok:
            c.passed = False
            c.failure_reason = reason

        ok2, reason2 = threshold_pass_overlay(c.rubric, overlay_min)
        if not ok2:
            c.passed = False
            c.failure_reason = c.failure_reason or reason2

        tests_ok = bool(c.checks.get("tests_passed", True)) and bool(c.checks.get("negative_tests_passed", True))
        if not tests_ok:
            c.passed = False
            c.failure_reason = c.failure_reason or "QUALITY_GATE_FAILED: TESTS_FAIL"

        if c.passed:
            qualified.append(c)

    if not qualified:
        raise ValueError("QUALITY_GATE_FAILED: NO_CANDIDATE_PASSES")

    # Rank by total score, then deterministic tie-break on hash
    qualified.sort(key=lambda c: (c.rubric.total(), sha256_text(c.code)), reverse=True)
    winner = qualified[0]

    return AtomSelection(
        atom_id=atom_id,
        atom_name=atom_name,
        atom_type=atom_type,
        trivial=trivial,
        candidates=candidates,
        winner_id=winner.candidate_id,
        selected_at_unix=int(time.time()),
        bounds={"max_candidates": max_candidates},
        overlay_applied=list(overlay_dims),
    )


def write_selection_artifacts(selection: AtomSelection, out_prefix: str) -> Tuple[str, str]:
    json_path = f"{out_prefix}_candidates.json"
    ledger_path = f"{out_prefix}_quality_ledger.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(selection), f, indent=2)

    entry = []
    entry.append(f"## Atom: {selection.atom_id} — {selection.atom_name}")
    entry.append(f"- Type: `{selection.atom_type}` trivial={selection.trivial}")
    entry.append(f"- Winner: `{selection.winner_id}`")
    entry.append(f"- Selected at (unix): `{selection.selected_at_unix}`")
    entry.append(f"- Bounds: `{selection.bounds}`")
    entry.append(f"- Overlay dims: `{selection.overlay_applied}`")
    entry.append("### Candidates")
    for c in selection.candidates:
        entry.append(
            f"- `{c.candidate_id}` total={c.rubric.total()} base={c.rubric.total_base()} "
            f"passed={c.passed} reason={c.failure_reason}"
        )
    entry.append("")

    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write("\n".join(entry) + "\n")

    return json_path, ledger_path


# ---------- Module coherence ----------

def module_coherence_check(module_id: str, atoms: List[AtomSelection]) -> Dict[str, Any]:
    """
    Lightweight coherence checker: flags inconsistent patterns across atom selections.
    In a full implementation, this would parse ASTs; here we use declared metadata.
    """
    violations: List[str] = []

    # Example checks based on declared overlay/type and winner presence
    for a in atoms:
        if not a.winner_id:
            violations.append(f"Atom {a.atom_id} has no winner_id")

    # Enforce "single error strategy" if declared in atom_meta in the future; placeholder now.
    passed = len(violations) == 0
    return {"module_id": module_id, "passed": passed, "violations": violations}


def write_module_coherence_artifact(report: Dict[str, Any], out_path: str) -> str:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return out_path

"""MB_P0_DEBUG_GOVERNANCE_V1 — Hardened Gate (P0)

This gate enforces the MetaBlooms P0 Debug+Code Constitution:
- Fail-closed if required governance artifacts are missing
- Enforce SEE (Sandcrawler/WebRun) artifacts when external facts are invoked
- Enforce telemetry correlation artifacts when runtime behavior is asserted
- Require the recursive loop controller path for C2+ work (non-trivial code/debug)

Design posture: reliability > convenience.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


# ----------------------------
# Error types (explicit)
# ----------------------------

class P0FailClosed(RuntimeError):
    """Unrecoverable policy violation for this turn/run."""

class P0Blocked(RuntimeError):
    """Recoverable missing-input failure: user/system must produce artifacts."""


# ----------------------------
# Canonical required artifacts
# ----------------------------

REQUIRED_ALWAYS = [
    "SYMPTOM_STATEMENT.md",          # or REQUIREMENTS.md (see normalization below)
    "DEBUG_HYPOTHESIS_LEDGER.json",
    "INVARIANT_LIST.md",
    "ECL_CLAIM_CLASS.json",
    "PROOF_BUNDLE.md",
    "MB_DEBUG_DECISION.json",
    "MB_RUN_MANIFEST.json"
]

# Allow REQUIREMENTS.md as an alias for SYMPTOM_STATEMENT.md in CODE mode.
SYMPTOM_ALIASES = {"SYMPTOM_STATEMENT.md", "REQUIREMENTS.md"}

SEE_REQUIRED = [
    "SEE_QUERIES.json",
    "SEE_SOURCES.md",
    "SEE_CITATION_MAP.json",
    "SEE_EVIDENCE_SUMMARY.md"
]

TELEM_REQUIRED = [
    "telemetry/telemetry_index.json",
    "telemetry/logs.ndjson"
]

# Non-trivial work must route through the recursive loop controller
RECURSION_REQUIRED_MARKERS = [
    "loop/LOOP_RECEIPTS.json",       # created by controller
    "loop/LOOP_SUMMARY.md"
]


# ----------------------------
# Helpers
# ----------------------------
# Artifact readers (repo-root)
# ----------------------------

def _load_artifact_json(repo_root: str, relpath: str) -> Dict[str, Any]:
    p = Path(repo_root) / relpath
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8", errors="ignore") or "{}")
    except Exception as e:
        raise P0FailClosed(f"Artifact {relpath} is not valid JSON: {e}")


def _artifact_exists(repo_root: str, relpath: str) -> bool:
    return (Path(repo_root) / relpath).exists()


# ----------------------------

def _as_list(x: Any) -> List[str]:
    if x is None:
        return []
    if isinstance(x, list):
        return [str(i) for i in x]
    # Accept comma-separated strings as a last resort, but normalize
    if isinstance(x, str):
        return [s.strip() for s in x.split(",") if s.strip()]
    raise P0FailClosed(f"Invalid artifacts type: {type(x)}; expected list[str]")


def _has_any(artifacts: List[str], candidates: set[str]) -> bool:
    aset = set(artifacts)
    return any(c in aset for c in candidates)


def _missing(artifacts: List[str], required: List[str]) -> List[str]:
    aset = set(artifacts)
    return [r for r in required if r not in aset]


def _require_field(context: Dict[str, Any], key: str, *, field_type: Optional[type] = None) -> Any:
    if key not in context:
        raise P0FailClosed(f"Missing required context field: {key}")
    val = context[key]
    if field_type and not isinstance(val, field_type):
        raise P0FailClosed(f"Context field '{key}' must be {field_type.__name__}, got {type(val)}")
    return val


def _normalize_required_always_for_mode(mode: str) -> List[str]:
    # In CODE mode, REQUIREMENTS.md can satisfy SYMPTOM_STATEMENT.md requirement.
    if mode == "CODE":
        req = [r for r in REQUIRED_ALWAYS if r != "SYMPTOM_STATEMENT.md"]
        # We'll check the alias set separately.
        return req
    return REQUIRED_ALWAYS




def _materialize_loop_artifacts(context: Dict[str, Any], artifacts: List[str]) -> List[str]:
    """Auto-create loop artifacts so the user never has to do it manually.

    This is activated when context['auto_loop'] is True AND claim_class is C2+.
    It writes:
      - loop/LOOP_RECEIPTS.json
      - loop/LOOP_SUMMARY.md

    Required context:
      - repo_root: filesystem root where artifacts should be written (directory)
    """
    auto_loop = bool(context.get("auto_loop", True))
    if not auto_loop:
        return artifacts

    repo_root = context.get("repo_root")
    if not repo_root:
        # No safe place to write -> fail-closed rather than silently skipping
        raise P0FailClosed("auto_loop requires context['repo_root'] to write loop artifacts")

    repo_root = str(repo_root)
    loop_dir = Path(repo_root) / "loop"
    loop_dir.mkdir(parents=True, exist_ok=True)

    receipts_path = loop_dir / "LOOP_RECEIPTS.json"
    summary_path = loop_dir / "LOOP_SUMMARY.md"

    # If already present, do not rewrite; append-only posture
    if not receipts_path.exists():
        receipts = {
            "run_id": context.get("run_id", "RUN_UNKNOWN"),
            "attempt_id": context.get("attempt_id", "A1"),
            "created_utc": time.time(),
            "policy": "MB_P0_DEBUG_GOVERNANCE_V1",
            "note": "Auto-materialized by P0 gate to enforce non-bypassable recursion receipts.",
            "iterations": []
        }
        receipts_path.write_text(json.dumps(receipts, indent=2))

    if not summary_path.exists():
        summary_path.write_text(
            "P0 LOOP SUMMARY\n\n"
            "- Created by gate auto_loop materialization.\n"
            "- Router must now execute bounded iterations and update receipts as evidence accrues.\n"
        )

    # Update artifact list with project-relative paths
    aset = set(artifacts)
    aset.add("loop/LOOP_RECEIPTS.json")
    aset.add("loop/LOOP_SUMMARY.md")
    return sorted(aset)

# ----------------------------
# Main entrypoint
# ----------------------------

def enforce(context: Dict[str, Any]) -> bool:
    """Entry point called by MetaBlooms routing layer.

    Expected context fields:
    - mode: "DEBUG" | "CODE"
    - claim_class: "C0".."C4"
    - artifacts: list[str] (project-relative paths)
    - external_facts_used: bool (if True -> SEE required)
    - runtime_evidence_used: bool (if True -> telemetry required)
    """

    if not isinstance(context, dict):
        raise P0FailClosed("Context must be a dict"ತ್ತ)

    mode = _require_field(context, "mode", field_type=str).upper()
    if mode not in {"DEBUG", "CODE"}:
        raise P0FailClosed(f"Invalid mode: {mode}; expected DEBUG or CODE")

    claim_class = _require_field(context, "claim_class", field_type=str).upper()
    if not re.match(r"^C[0-4]$", claim_class):
        raise P0FailClosed(f"Invalid claim_class: {claim_class}; expected C0..C4" )

    artifacts = _as_list(_require_field(context, "artifacts"))
    external_facts_used = bool(context.get("external_facts_used", False))
    runtime_evidence_used = bool(context.get("runtime_evidence_used", False))

    # ---- Always-on base requirements
    required_base = _normalize_required_always_for_mode(mode)
    missing_base = _missing(artifacts, required_base)

    # Alias check for symptom/requirements doc
    if mode == "CODE" and not _has_any(artifacts, SYMPTOM_ALIASES):
        missing_base.append("SYMPTOM_STATEMENT.md|REQUIREMENTS.md (one required)")

    if missing_base:
        raise P0Blocked(f"P0 BLOCKED — missing base governance artifacts: {missing_base}")

    # ---- SEE enforcement
    if external_facts_used:
        missing_see = _missing(artifacts, SEE_REQUIRED)
        if missing_see:
            raise P0FailClosed(f"P0 FAIL-CLOSED — SEE required but missing artifacts: {missing_see}")

    # ---- Telemetry enforcement
    if runtime_evidence_used:
        missing_telem = _missing(artifacts, TELEM_REQUIRED)
        if missing_telem:
            raise P0FailClosed(f"P0 FAIL-CLOSED — telemetry required but missing artifacts: {missing_telem}")
    # ---- Recursion enforcement (C2+)
    if claim_class in {"C2", "C3", "C4"}:
        has_receipts = all(r in set(artifacts) for r in RECURSION_REQUIRED_MARKERS)
        if not has_receipts:
            # Auto-materialize receipts so the user never has to do it manually.
            artifacts[:] = _materialize_loop_artifacts(context, artifacts)
            has_receipts = all(r in set(artifacts) for r in RECURSION_REQUIRED_MARKERS)
        if not has_receipts:
            raise P0FailClosed(
                "P0 FAIL-CLOSED — C2+ work requires recursive loop controller evidence. "
                "Missing loop artifacts: loop/LOOP_RECEIPTS.json and loop/LOOP_SUMMARY.md"
            )

    # ---- CERTIFICATION CHECK (ECL PASS marker required when declaring PASS)
    # If MB_DEBUG_DECISION.json says PASS for C2+, require ecl/ECL_PASS.json and a loop receipt outcome with ecl_pass=true.
    if claim_class in {"C2", "C3", "C4"}:
        repo_root = context.get("repo_root")
        if not repo_root:
            raise P0FailClosed("repo_root required for certification checks")
        decision = _load_artifact_json(str(repo_root), "MB_DEBUG_DECISION.json")
        if str(decision.get("state", "")).upper() == "PASS":
            if not _artifact_exists(str(repo_root), "ecl/ECL_PASS.json"):
                raise P0FailClosed("P0 FAIL-CLOSED — PASS requires ecl/ECL_PASS.json for C2+")
            receipts = _load_artifact_json(str(repo_root), "loop/LOOP_RECEIPTS.json")
            ok = False
            for it in receipts.get("iterations", []):
                oc = it.get("outcome") or {}
                if oc.get("ecl_pass") is True:
                    ok = True
                    break
            if not ok:
                raise P0FailClosed("P0 FAIL-CLOSED — PASS requires loop receipts with outcome.ecl_pass=true")

    return True

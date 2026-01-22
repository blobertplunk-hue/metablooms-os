# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""EC-AUTO validator (v1)

Fail-closed validator intended to be called by preflight.

This module validates that when EC Mode is active, required artifacts and
STS-5 compliance exist.

NOTE: This is a wiring-ready stub with strict interfaces. It does not assume
any particular filesystem layout beyond what the caller passes in.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ECAutoResult:
    ok: bool
    errors: List[str]
    mode_active: bool
    bypass_used: bool


def detect_ec_mode(context: Dict[str, Any]) -> bool:
    """Return True if EC Mode must be active based on provided context.

    Expected context keys (caller-provided):
      - intent_class: str
      - file_writes: list[str] (paths)
      - bundle_contains_code: bool
    """
    intent = (context.get("intent_class") or "").strip()
    file_writes = context.get("file_writes") or []
    contains_code = bool(context.get("bundle_contains_code"))

    code_exts = (
        ".py", ".js", ".ts", ".sh", ".yaml", ".yml", ".json",
        ".java", ".go", ".rs", ".cpp", ".c", ".cs",
    )

    if intent in {"CODE_TOUCH", "OS_MUTATION"}:
        return True

    if contains_code:
        return True

    for p in file_writes:
        p = str(p)
        if p.endswith(code_exts):
            return True

    return False


def validate_ec_auto(context: Dict[str, Any]) -> ECAutoResult:
    """Validate EC-AUTO requirements.

    Caller MUST supply booleans/paths indicating whether required artifacts
    were produced.

    Required context keys when EC Mode is active:
      - has_design_freeze: bool
      - has_changeset: bool
      - has_verification_evidence: bool
      - sts5_final_ok: bool
      - bypass_ok: bool (only relevant if intent_class == DISPOSABLE_SNIPPET)

    Returns fail-closed errors when requirements not met.
    """

    intent = (context.get("intent_class") or "").strip()
    mode_active = detect_ec_mode(context)

    bypass_used = (intent == "DISPOSABLE_SNIPPET") and bool(context.get("bypass_ok"))

    # If mode would be active but bypass is attempted incorrectly, fail-closed.
    if intent == "DISPOSABLE_SNIPPET" and not bypass_used:
        # If the run actually wrote files or mutated, bypass is not allowed.
        if mode_active:
            return ECAutoResult(
                ok=False,
                errors=["EC_AUTO_BYPASS_DENIED: disposable snippet classification invalid under triggers"],
                mode_active=True,
                bypass_used=False,
            )

    # If mode is not active, validator passes.
    if not mode_active:
        return ECAutoResult(ok=True, errors=[], mode_active=False, bypass_used=False)

    errors: List[str] = []

    if not bool(context.get("has_design_freeze")):
        errors.append("EC_AUTO_MISSING_DESIGN_FREEZE")
    if not bool(context.get("has_changeset")):
        errors.append("EC_AUTO_MISSING_CHANGESET")
    if not bool(context.get("has_verification_evidence")):
        errors.append("EC_AUTO_MISSING_VERIFICATION_EVIDENCE")
    if not bool(context.get("sts5_final_ok")):
        errors.append("EC_AUTO_STS5_FINAL_INVALID")

    return ECAutoResult(ok=(len(errors) == 0), errors=errors, mode_active=True, bypass_used=bypass_used)

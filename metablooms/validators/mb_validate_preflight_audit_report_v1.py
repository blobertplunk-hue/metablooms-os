# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms validator: preflight audit report schema (v1).

Fail-closed validator to prevent audit-report drift.

Validates the JSON report produced by a preflight gate audit procedure before it
is packaged and published.

Returns a list of human-readable error strings.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple, Union

REQUIRED_TOP_KEYS: Dict[str, Union[type, Tuple[type, ...]]] = {
    "bundle": str,
    "audit_timestamp": str,
    "chain_path": str,
    "chain_version": (str, int, type(None)),
    "gate_count": int,
    "available_gate_modules": dict,
    "gate_entries": list,
    "findings": list,
    "overall": str,
}

ALLOWED_OVERALL = {"PASS", "FAIL"}
ALLOWED_FINDING_SEVERITY = {"WARN", "FAIL"}


def _type_ok(value: Any, expected: Union[type, Tuple[type, ...]]) -> bool:
    return isinstance(value, expected)


def validate_report(obj: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(obj, dict):
        return ["report is not a dict"]

    for key, expected_type in REQUIRED_TOP_KEYS.items():
        if key not in obj:
            errors.append(f"missing top-level key: {key}")
            continue
        if not _type_ok(obj[key], expected_type):
            errors.append(
                f"bad type for {key}: expected {expected_type}, got {type(obj[key]).__name__}"
            )

    overall = obj.get("overall")
    if isinstance(overall, str) and overall not in ALLOWED_OVERALL:
        errors.append(f"overall must be one of {sorted(ALLOWED_OVERALL)}")

    findings = obj.get("findings")
    if isinstance(findings, list):
        for i, f in enumerate(findings):
            if not isinstance(f, dict):
                errors.append(f"findings[{i}] is not a dict")
                continue
            severity = f.get("severity")
            if severity not in ALLOWED_FINDING_SEVERITY:
                errors.append(f"findings[{i}].severity missing/invalid")
            code = f.get("code")
            if not isinstance(code, str) or not code:
                errors.append(f"findings[{i}].code missing/invalid")
            if "details" not in f:
                errors.append(f"findings[{i}].details missing")

    return errors

"""
ECL — Extraordinary Coding Law
================================

ECL enforces truthful, deterministic, evidence-first behavior.
Violations are BLOCKING by default.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any


class ECLSeverity(str, Enum):
    WARN = "WARN"
    BLOCK = "BLOCK"


class ECLViolationType(str, Enum):
    MISSING_ECL_HEADER = "MISSING_ECL_HEADER"
    UNDECLARED_SIDE_EFFECT = "UNDECLARED_SIDE_EFFECT"
    CLAIM_WITHOUT_EVIDENCE = "CLAIM_WITHOUT_EVIDENCE"
    NON_DETERMINISTIC_OUTPUT = "NON_DETERMINISTIC_OUTPUT"


@dataclass(frozen=True)
class ECLViolation:
    violation_type: ECLViolationType
    severity: ECLSeverity
    message: str
    context: Dict[str, Any]


class ECLResult:
    def __init__(self, violations: List[ECLViolation]):
        self.violations = violations
        self.has_blockers = any(v.severity == ECLSeverity.BLOCK for v in violations)


REQUIRED_ECL_HEADERS = {
    "ECL_VERSION",
    "ECL_SCOPE",
    "ECL_RESPONSIBILITY",
}


def check_ecl_headers(module_globals: Dict[str, Any]) -> List[ECLViolation]:
    violations = []
    missing = REQUIRED_ECL_HEADERS - set(module_globals.keys())
    if missing:
        violations.append(
            ECLViolation(
                violation_type=ECLViolationType.MISSING_ECL_HEADER,
                severity=ECLSeverity.BLOCK,
                message=f"Missing required ECL headers: {sorted(missing)}",
                context={"missing": sorted(missing)},
            )
        )
    return violations


def check_claims_have_evidence(claims: List[Any], evidence_pointers: List[Any]) -> List[ECLViolation]:
    violations = []
    if claims and not evidence_pointers:
        violations.append(
            ECLViolation(
                violation_type=ECLViolationType.CLAIM_WITHOUT_EVIDENCE,
                severity=ECLSeverity.BLOCK,
                message="Claims exist but no evidence pointers were produced.",
                context={"claim_count": len(claims)},
            )
        )
    return violations


def check_determinism(run_hashes: List[str]) -> List[ECLViolation]:
    violations = []
    if len(set(run_hashes)) > 1:
        violations.append(
            ECLViolation(
                violation_type=ECLViolationType.NON_DETERMINISTIC_OUTPUT,
                severity=ECLSeverity.BLOCK,
                message="Multiple differing output hashes detected for same inputs.",
                context={"hashes": run_hashes},
            )
        )
    return violations


def run_ecl_checks(
    *,
    module_globals: Dict[str, Any],
    claims: List[Any],
    evidence_pointers: List[Any],
    run_hashes: List[str],
) -> ECLResult:
    violations: List[ECLViolation] = []
    violations.extend(check_ecl_headers(module_globals))
    violations.extend(check_claims_have_evidence(claims, evidence_pointers))
    violations.extend(check_determinism(run_hashes))
    return ECLResult(violations)

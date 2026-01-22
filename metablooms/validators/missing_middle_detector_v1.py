"""Missing Middle Detector (MMD) v1.

Purpose
Detects "missing middle" gaps between:
- PLAN -> CODE
- CODE -> EVIDENCE
- EVIDENCE -> GATE
- LOOP completeness
- SECURITY validation (filesystem + execution hardening)

Design
- Deterministic heuristics.
- Fail-closed for P0 security gaps.
- Emits machine-readable findings.
"""

from __future__ import annotations

import json
import os
import hashlib
from typing import Any, Dict, List

FINDING = Dict[str, Any]

# Canonical required components for SEE recursive improvement.
REQUIRED_PATHS = [
    # Loop + runtime
    "metablooms/loop/see_recursive_controller_v1.py",
    "metablooms/runtime/sandbox_exec_v1.py",
    # Evidence core
    "metablooms/evidence/store_v1.py",
    "metablooms/evidence/receipt_validate_v1.py",
    "metablooms/evidence/regression_signature_v1.py",
    # Diagnostics + patching
    "metablooms/diagnostics/failure_diagnoser_v1.py",
    "metablooms/patching/patch_provider_v1.py",
    # Security utilities
    "metablooms/security/path_safety_v1.py",
    # Concurrency utilities
    "metablooms/concurrency/lock_v1.py",
    # Schemas
    "metablooms/schemas/see_receipt_v1.schema.json",
    "metablooms/schemas/missing_middle_finding_v1.json",
    # Gate
    "metablooms/preflight/gates/mb_gate_evidence_see_loop_v1.py",
]

REQUIRED_GATE_ID = "GATE.EVIDENCE.SEE.LOOP.V1"
GATE_CHAIN_REL = "metablooms/preflight/preflight_gate_chain_v1.json"


def _exists(root: str, rel: str) -> bool:
    return os.path.exists(os.path.join(root, rel))


def _read_text(root: str, rel: str) -> str:
    p = os.path.join(root, rel)
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def _finding(
    *,
    severity: str,
    category: str,
    missing: str | None = None,
    detail: str | None = None,
) -> FINDING:
    # Deterministic finding_id: stable across runs for the same condition.
    seed = f"{severity}|{category}|{missing or ''}|{detail or ''}".encode("utf-8")
    finding_id = "MM-" + hashlib.sha1(seed).hexdigest()[:10]

    msg = f"{category}: {missing or ''} {detail or ''}".strip()

    out: FINDING = {
        "finding_id": finding_id,
        "severity": severity,
        "category": category,
        "message": msg,
    }
    if isinstance(missing, str):
        out["missing"] = missing
    if isinstance(detail, str):
        out["detail"] = detail
    return out


def _detect_required_paths(root: str) -> List[FINDING]:
    findings: List[FINDING] = []
    for rel in REQUIRED_PATHS:
        if not _exists(root, rel):
            findings.append(_finding(severity="BLOCK", category="PLAN_CODE", missing=rel))
    return findings


def _detect_gate_chain_registration(root: str) -> List[FINDING]:
    findings: List[FINDING] = []
    if not _exists(root, GATE_CHAIN_REL):
        return [_finding(severity="BLOCK", category="EVIDENCE_GATE", missing=GATE_CHAIN_REL)]

    try:
        with open(os.path.join(root, GATE_CHAIN_REL), "r", encoding="utf-8") as f:
            chain = json.load(f)
    except Exception as e:  # noqa: BLE001
        return [_finding(severity="BLOCK", category="EVIDENCE_GATE", missing=GATE_CHAIN_REL, detail=str(e))]

    # Chain may be a dict wrapper {"gates": [...]} or a bare list [...].
    if isinstance(chain, list):
        gates = chain
    elif isinstance(chain, dict):
        gates = chain.get("gates", [])
    else:
        gates = []

    present = set(
        g.get("id") for g in gates if isinstance(g, dict) and isinstance(g.get("id"), str)
    )

    if REQUIRED_GATE_ID not in present:
        findings.append(
            _finding(
                severity="BLOCK",
                category="EVIDENCE_GATE",
                detail=f"MISSING_GATE_ID:{REQUIRED_GATE_ID}",
            )
        )

    # If present, ensure module path is correct and byte-present.
    for g in gates:
        if not isinstance(g, dict):
            continue
        if g.get("id") != REQUIRED_GATE_ID:
            continue
        mod = g.get("module")
        if isinstance(mod, str):
            # Expected module is metablooms.preflight.gates.mb_gate_evidence_see_loop_v1
            if "mb_gate_evidence_see_loop_v1" not in mod:
                findings.append(
                    _finding(
                        severity="BLOCK",
                        category="EVIDENCE_GATE",
                        detail=f"GATE_MODULE_MISMATCH:{mod}",
                    )
                )
        break

    return findings


def _detect_security_validation(root: str) -> List[FINDING]:
    """Security missing-middle axis.

    Heuristics (deterministic):
    - EvidenceStore must use the path_safety module.
    - EvidenceStore must enforce safe component + join-under semantics.

    If these are absent, it is a BLOCK (path traversal risk).
    """

    findings: List[FINDING] = []

    store_rel = "metablooms/evidence/store_v1.py"
    sec_rel = "metablooms/security/path_safety_v1.py"

    if not _exists(root, store_rel):
        return findings  # PLAN_CODE will catch; avoid duplicates.

    if not _exists(root, sec_rel):
        findings.append(_finding(severity="BLOCK", category="SECURITY_VALIDATION", missing=sec_rel))
        return findings

    text = _read_text(root, store_rel)
    required_tokens = ["path_safety_v1", "safe_component", "safe_join_under"]
    missing_tokens = [t for t in required_tokens if t not in text]
    if missing_tokens:
        findings.append(
            _finding(
                severity="BLOCK",
                category="SECURITY_VALIDATION",
                missing=store_rel,
                detail=f"MISSING_SECURITY_TOKENS:{missing_tokens}",
            )
        )

    return findings


def _detect_patch_provider_stub(root: str) -> List[FINDING]:
    """Warn when recursive improvement is claimed but patch provider is inert."""
    rel = "metablooms/patching/patch_provider_v1.py"
    if not _exists(root, rel):
        return []

    text = _read_text(root, rel)
    # Heuristic: if provide_patch returns None with no branching, treat as stub.
    if "def provide_patch" in text and "return None" in text and "if " not in text:
        return [
            _finding(
                severity="WARN",
                category="CAPABILITY_COMPLETENESS",
                missing=rel,
                detail="PATCH_PROVIDER_STUB:return None",
            )
        ]

    return []


def _detect_resource_management(root: str) -> List[FINDING]:
    """Resource management missing-middle axis.

    Checks for bounded evidence writes to prevent disk/inode exhaustion.
    """
    findings: List[FINDING] = []

    store_rel = "metablooms/evidence/store_v1.py"
    if not _exists(root, store_rel):
        return findings

    text = _read_text(root, store_rel).lower()
    required = ["disk_usage", "min_free_bytes", "max_artifact_bytes", "max_total_task_bytes"]
    missing = [t for t in required if t not in text]
    if missing:
        findings.append(
            _finding(
                severity="WARN",
                category="RESOURCE_MANAGEMENT",
                missing=store_rel,
                detail=f"MISSING_RESOURCE_TOKENS:{missing}",
            )
        )
    return findings


def _detect_concurrency_safety(root: str) -> List[FINDING]:
    """Concurrency safety axis.

    Checks for locking around evidence directory allocation and receipt writes.
    """
    findings: List[FINDING] = []
    lock_rel = "metablooms/concurrency/lock_v1.py"
    store_rel = "metablooms/evidence/store_v1.py"
    if not _exists(root, lock_rel):
        findings.append(_finding(severity="BLOCK", category="CONCURRENCY_SAFETY", missing=lock_rel))
        return findings
    if not _exists(root, store_rel):
        return findings
    text = _read_text(root, store_rel)
    if "FileLock" not in text and "flock" not in text:
        findings.append(
            _finding(
                severity="BLOCK",
                category="CONCURRENCY_SAFETY",
                missing=store_rel,
                detail="MISSING_LOCKING:EvidenceStore must lock per artifact_id",
            )
        )
    return findings


def _detect_error_handling(root: str) -> List[FINDING]:
    """Error handling axis.

    Checks that executor fail paths are captured into evidence, avoiding fail-open.
    """
    findings: List[FINDING] = []
    rel = "metablooms/runtime/sandbox_exec_v1.py"
    if not _exists(root, rel):
        return findings
    text = _read_text(root, rel)
    required = ["TimeoutExpired", "SANDBOX_EXEC_EXCEPTION", "EVIDENCE_IO_FAILED"]
    missing = [t for t in required if t not in text]
    if missing:
        findings.append(
            _finding(
                severity="WARN",
                category="ERROR_HANDLING",
                missing=rel,
                detail=f"MISSING_ERROR_TOKENS:{missing}",
            )
        )
    return findings


def _detect_schema_enforcement(root: str) -> List[FINDING]:
    """Schema enforcement axis.

    Checks that receipt validation uses JSON Schema validation (prevents drift).
    """
    findings: List[FINDING] = []
    rel = "metablooms/evidence/receipt_validate_v1.py"
    if not _exists(root, rel):
        return findings
    text = _read_text(root, rel)
    required = ["import jsonschema", "jsonschema.validate"]
    missing = [t for t in required if t not in text]
    if missing:
        findings.append(
            _finding(
                severity="WARN",
                category="SCHEMA_ENFORCEMENT",
                missing=rel,
                detail=f"MISSING_SCHEMA_VALIDATION:{missing}",
            )
        )
    return findings


def _detect_environment_portability(root: str) -> List[FINDING]:
    """ENVIRONMENT_PORTABILITY axis.

    The lock primitive should be available on both POSIX and Windows.
    Heuristic: lock_v1.py contains both 'fcntl' and 'msvcrt' imports (guarded).
    """
    findings: List[FINDING] = []

    rel = "metablooms/concurrency/lock_v1.py"
    lock_path = os.path.join(root, "metablooms", "concurrency", "lock_v1.py")
    if not os.path.exists(lock_path):
        return [
            {
                "severity": "BLOCK",
                "category": "ENVIRONMENT_PORTABILITY",
                "missing": "metablooms/concurrency/lock_v1.py",
            }
        ]

    txt = _read_text(root, rel)
    has_fcntl = "fcntl" in txt
    has_msvcrt = "msvcrt" in txt
    if not (has_fcntl and has_msvcrt):
        findings.append(
            {
                "severity": "BLOCK",
                "category": "ENVIRONMENT_PORTABILITY",
                "missing": "lock_v1.py should include both POSIX (fcntl) and Windows (msvcrt) backends",
            }
        )

    return findings


def _detect_configuration_management(root: str) -> List[FINDING]:
    """CONFIGURATION_MANAGEMENT axis.

    Resource limits should be externally tunable to support constrained environments.
    """
    findings: List[FINDING] = []
    cfg_json = os.path.join(root, "metablooms", "config", "resource_limits_v1.json")
    cfg_loader = os.path.join(root, "metablooms", "config", "load_config_v1.py")
    if not os.path.exists(cfg_json):
        findings.append(
            {
                "severity": "WARN",
                "category": "CONFIGURATION_MANAGEMENT",
                "missing": "metablooms/config/resource_limits_v1.json",
            }
        )
    if not os.path.exists(cfg_loader):
        findings.append(
            {
                "severity": "WARN",
                "category": "CONFIGURATION_MANAGEMENT",
                "missing": "metablooms/config/load_config_v1.py",
            }
        )

    # Ensure EvidenceStore references the loader (heuristic)
    store_rel = "metablooms/evidence/store_v1.py"
    store_path = os.path.join(root, "metablooms", "evidence", "store_v1.py")
    if os.path.exists(store_path):
        txt = _read_text(root, store_rel)
        if "load_resource_limits" not in txt:
            findings.append(
                {
                    "severity": "WARN",
                    "category": "CONFIGURATION_MANAGEMENT",
                    "missing": "EvidenceStore should use load_resource_limits() to avoid hard-coded thresholds",
                }
            )

    return findings


def _detect_dependency_management(root: str) -> List[FINDING]:
    """DEPENDENCY_MANAGEMENT axis.

    If MetaBlooms imports non-stdlib modules, requirements.txt must exist and name them.
    Fail-closed: missing requirements.txt is BLOCK when non-stdlib imports are present.
    """
    findings: List[FINDING] = []
    req_path = os.path.join(root, "requirements.txt")

    # Minimal import scan (keep deterministic; avoid AST edge cases)
    nonstdlib = set()
    for rel in [
        "metablooms/evidence/receipt_validate_v1.py",
        "metablooms/validators/missing_middle_detector_v1.py",
    ]:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        txt = _read_text(root, rel)
        if "import jsonschema" in txt or "from jsonschema" in txt:
            nonstdlib.add("jsonschema")

    if nonstdlib and (not os.path.exists(req_path)):
        findings.append(
            {
                "severity": "BLOCK",
                "category": "DEPENDENCY_MANAGEMENT",
                "missing": "requirements.txt (jsonschema required)",
            }
        )
        return findings

    if nonstdlib and os.path.exists(req_path):
        req_txt = _read_text(root, "requirements.txt")
        for dep in sorted(nonstdlib):
            if dep not in req_txt:
                findings.append(
                    {
                        "severity": "BLOCK",
                        "category": "DEPENDENCY_MANAGEMENT",
                        "missing": f"requirements.txt missing dependency: {dep}",
                    }
                )

    return findings


def detect_missing_middle(root: str) -> List[FINDING]:
    """Return a list of missing-middle findings."""
    root = os.path.abspath(root)

    findings: List[FINDING] = []
    findings.extend(_detect_required_paths(root))
    findings.extend(_detect_gate_chain_registration(root))
    findings.extend(_detect_security_validation(root))
    findings.extend(_detect_patch_provider_stub(root))
    findings.extend(_detect_resource_management(root))
    findings.extend(_detect_concurrency_safety(root))
    findings.extend(_detect_error_handling(root))
    findings.extend(_detect_schema_enforcement(root))
    findings.extend(_detect_environment_portability(root))
    findings.extend(_detect_configuration_management(root))
    findings.extend(_detect_dependency_management(root))

    return findings
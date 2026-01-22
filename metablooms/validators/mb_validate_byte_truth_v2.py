# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Validator: BYTE_TRUTH (v2)

Purpose
- Prevent design-side state fabrication by asserting that the OS is byte-present,
  non-trivial, and structurally plausible *in the current execution environment*.

This validator is intentionally conservative. It does not attempt to infer intent.
It only checks filesystem evidence.

Key rule (BYTE_TRUTH.V2)
- If the bytes are not present on disk, the system must not claim they exist.

Signals (fail-closed)
- Missing required paths (e.g., BOOT_METABLOOMS.py, metablooms/).
- OS root total size below a configured minimum (stub / scaffold detection).

Notes
- This validator is designed to be used as a P0 preflight gate.
- It does not require any network access.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Iterable, List, Optional


@dataclass
class Finding:
    path: str
    kind: str
    detail: str


@dataclass
class Result:
    ok: bool
    total_bytes: int
    findings: List[Finding] = field(default_factory=list)


def _walk_bytes(root: str) -> int:
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                total += os.path.getsize(p)
            except OSError:
                # If we cannot stat a file, treat as 0 bytes; the caller will also
                # see a missing/permission issue via required-path checks if relevant.
                pass
    return total


def _require_path(root: str, rel: str, findings: List[Finding]) -> None:
    p = os.path.join(root, rel)
    if not os.path.exists(p):
        findings.append(Finding(path=rel, kind="MISSING_REQUIRED_PATH", detail="not found"))


def validate_byte_truth_v2(
    root: str,
    *,
    min_os_bytes: int = 1_000_000,
    required_paths: Optional[Iterable[str]] = None,
) -> Result:
    """Validate byte-truth properties for an OS root directory.

    Args:
        root: OS root path.
        min_os_bytes: Lower bound for considering an OS "non-stub".
        required_paths: Relative paths that must exist.

    Returns:
        Result with ok=False if any finding exists.
    """

    findings: List[Finding] = []

    if not root or not os.path.isdir(root):
        findings.append(Finding(path=str(root), kind="ROOT_NOT_DIRECTORY", detail="root missing or not a directory"))
        return Result(ok=False, total_bytes=0, findings=findings)

    req = list(required_paths or [
        "BOOT_METABLOOMS.py",
        "metablooms",
        "SYSTEM_INDEX.json",
        "SHIP_MANIFEST.json",
    ])

    for rel in req:
        _require_path(root, rel, findings)

    total = _walk_bytes(root)

    if total < int(min_os_bytes):
        findings.append(Finding(path=".", kind="OS_TOO_SMALL", detail=f"total_bytes={total} < min_os_bytes={min_os_bytes}"))

    ok = len(findings) == 0
    return Result(ok=ok, total_bytes=total, findings=findings)

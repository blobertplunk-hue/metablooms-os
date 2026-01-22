# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# ECL:
#   id: EXCODE_ECL_VALIDATE_V1
#   role: validator
#   owns: [enforce_clarity_layer_contract]
#   does_not: [execute_user_code, mutate_runtime_state]
#   inputs: [root_path:str, mode:str]
#   outputs: [result:dict]
#   side_effects: [none]
#   failure_modes: [MISSING_HEADER, MISSING_DOCSTRING, MISSING_DOCSECTIONS]
#   invariants: [NO_EXEC_ON_IMPORT]
#   evidence: [returned result dict]
#   last_reviewed: 2026-01-16
"""Extraordinary Coding — Clarity Layer validator (v1)

Intent
Validate that source files comply with EXCODE_ECL_V1 so readers cannot be confused.

Scope
- Checks for presence of ECL header block
- Checks that the module docstring (top-of-file) contains required sections in order

Non-Goals
- Does not assess algorithmic correctness
- Does not import or execute scanned modules

Inputs
root_path (str): repository root to scan
mode (str): 'WARN' or 'FAIL'

Outputs
dict: {pass: bool, violations: [...], coverage: {...}}

Side Effects
None.

Failure Modes
MISSING_HEADER, MISSING_DOCSTRING, MISSING_DOCSECTIONS

Invariants
Validator is side-effect free and does not import scanned modules.

Evidence & Observability
Returned dict is the evidence artifact.

Examples
result = validate_repo('/path/to/os', mode='WARN')

Maintenance Notes
Extend EXCODE_ECL_V1 carefully; keep checks deterministic.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

PY_FILE_RE = re.compile(r'.*\.py$', re.IGNORECASE)
ECL_HEADER_RE = re.compile(r'^#\s*ECL\s*:\s*$', re.MULTILINE)

REQUIRED_DOC_SECTIONS = [
    "Intent",
    "Scope",
    "Non-Goals",
    "Inputs",
    "Outputs",
    "Side Effects",
    "Failure Modes",
    "Invariants",
    "Evidence & Observability",
    "Examples",
    "Maintenance Notes",
]

@dataclass
class Violation:
    path: str
    code: str
    detail: str

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()

def _has_ecl_header(text: str) -> bool:
    return bool(ECL_HEADER_RE.search(text))

def _extract_top_module_docstring(text: str) -> str:
    """Extract the first module docstring if it appears immediately after shebang/comments."""
    lines = text.splitlines()
    i = 0
    if lines and lines[0].startswith("#!"):
        i += 1
    # skip leading blank/comment lines
    while i < len(lines) and (lines[i].strip() == "" or lines[i].lstrip().startswith("#")):
        i += 1
    if i >= len(lines):
        return ""
    line = lines[i].lstrip()
    if line.startswith('"""') or line.startswith("'''"):
        quote = '"""' if line.startswith('"""') else "'''"
        # strip opening quotes
        buf = [line[len(quote):]]
        i += 1
        while i < len(lines):
            if quote in lines[i]:
                end = lines[i]
                buf.append(end[:end.find(quote)])
                return "\n".join(buf).strip()
            buf.append(lines[i])
            i += 1
    return ""

def _sections_in_order(doc: str) -> Tuple[bool, List[str]]:
    found: List[str] = []
    for raw in doc.splitlines():
        line = raw.strip()
        if line in REQUIRED_DOC_SECTIONS:
            found.append(line)
    if not found:
        return False, []
    pos = 0
    for req in REQUIRED_DOC_SECTIONS:
        try:
            j = found.index(req, pos)
        except ValueError:
            return False, found
        pos = j + 1
    return True, found

def validate_repo(root_path: str, mode: str = "WARN") -> Dict:
    violations: List[Violation] = []
    scanned = 0
    compliant = 0

    for root, _, files in os.walk(root_path):
        for fn in files:
            if not PY_FILE_RE.match(fn):
                continue
            path = os.path.join(root, fn)
            scanned += 1
            text = _read_text(path)

            ok = True
            if not _has_ecl_header(text):
                ok = False
                violations.append(Violation(path, "MISSING_HEADER", "ECL header block not found."))

            doc = _extract_top_module_docstring(text)
            if not doc:
                ok = False
                violations.append(Violation(path, "MISSING_DOCSTRING", "Top-of-file module docstring not found."))
            else:
                in_order, found = _sections_in_order(doc)
                if not in_order:
                    ok = False
                    violations.append(Violation(path, "MISSING_DOCSECTIONS", f"Doc sections missing/out-of-order. Found: {found}"))

            if ok:
                compliant += 1

    coverage = {
        "scanned_py_files": scanned,
        "compliant_py_files": compliant,
        "percent": (0.0 if scanned == 0 else round((compliant / scanned) * 100.0, 2)),
    }

    passed = True if mode.upper() == "WARN" else (coverage["percent"] >= 85.0)

    return {
        "pass": passed,
        "mode": mode.upper(),
        "coverage": coverage,
        "violations": [v.__dict__ for v in violations],
    }

# NOTE: ECL_QUALITY_SCAN_RESULT_V1 may be consumed as WARN-only when provided.

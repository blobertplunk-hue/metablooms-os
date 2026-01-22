# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Validator: NO_PLACEHOLDERS (v1)

Detect placeholder / omission markers and silent stubs in ship-path code.

Design goals
- Conservative and auditable (simple heuristics, easy to reason about).
- Avoid self-triggering (this module must not contain the literal marker tokens).

Signals
- Standalone omission ellipsis (a line that is only three dots).
- "Silent stub" bodies (a def/class whose first meaningful body line is a lone pass
  statement, except for marker exception classes).
- Common placeholder tokens (constructed programmatically to avoid self-trigger).

Scope (default): Python sources under the OS root, excluding docs/examples/tests
unless explicitly configured.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple


# NOTE: Construct token strings programmatically so this validator does not
# embed the literal markers it is designed to detect.
FORBIDDEN_TOKENS = [
    "TO" + "DO",
    "TB" + "D",
    "FIX" + "ME",
    "X" + "X" + "X",
    "HA" + "CK",
    "REPLACE" + "_" + "ME",
    "CHANGE" + "ME",
]

# Regexes
_RE_FORBIDDEN_TOKEN = re.compile(r"\b(" + "|".join(map(re.escape, FORBIDDEN_TOKENS)) + r")\b", re.IGNORECASE)
_RE_STANDALONE_ELLIPSIS = re.compile(r"^\s*\.\.\.\s*(#.*)?$")
_RE_DEF_LINE = re.compile(r"^\s*(def|class)\s+([A-Za-z_][A-Za-z0-9_]*)\b")
_RE_CLASS_EXCEPTION = re.compile(r"^\s*class\s+[A-Za-z_][A-Za-z0-9_]*\s*\(\s*Exception\s*\)\s*:\s*$")


@dataclass
class Finding:
    path: str
    line: int
    kind: str
    detail: str


@dataclass
class Result:
    ok: bool
    findings: List[Finding] = field(default_factory=list)


def _is_excluded_path(path: str, *, root: str, extra_excludes: Optional[Sequence[str]] = None) -> bool:
    rel = os.path.relpath(path, root).replace("\\", "/")
    if rel.startswith("docs/") or rel.startswith("examples/") or rel.startswith("tests/"):
        return True
    if extra_excludes:
        for ex in extra_excludes:
            exn = ex.replace("\\", "/").rstrip("/")
            if rel.startswith(exn + "/") or rel == exn:
                return True
    return False


def _iter_py_files(root: str, *, extra_excludes: Optional[Sequence[str]] = None) -> Iterable[str]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip hidden dirs and __pycache__
        dirnames[:] = [d for d in dirnames if not d.startswith(".") and d != "__pycache__"]
        for fn in filenames:
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            if _is_excluded_path(path, root=root, extra_excludes=extra_excludes):
                continue
            yield path


def _is_typing_ellipsis_line(line: str) -> bool:
    # Allow ellipsis inside []/() for typing contexts; this is a heuristic.
    # We only exempt lines where '...' appears inside brackets/parentheses and
    # not as a standalone statement.
    if "..." not in line:
        return False
    if _RE_STANDALONE_ELLIPSIS.match(line):
        return False
    # crude: if contains 'Callable[' or 'Tuple[' or 'list[' or 'dict[' etc and '...'
    return "..." in line and ("Callable" in line or "Tuple" in line)


def validate_no_placeholders(
    root: str,
    *,
    extra_excludes: Optional[Sequence[str]] = None,
) -> Result:
    findings: List[Finding] = []

    for path in _iter_py_files(root, extra_excludes=extra_excludes):
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:  # noqa: BLE001
            findings.append(Finding(path=path, line=0, kind="READ_ERROR", detail=str(e)))
            continue

        for i, line in enumerate(lines, start=1):
            # forbidden tokens
            m = _RE_FORBIDDEN_TOKEN.search(line)
            if m:
                findings.append(Finding(path=path, line=i, kind="FORBIDDEN_TOKEN", detail=m.group(0)))

            # ellipsis omission marker
            if "..." in line:
                if _RE_STANDALONE_ELLIPSIS.match(line) and not _is_typing_ellipsis_line(line):
                    findings.append(Finding(path=path, line=i, kind="ELLIPSIS_OMISSION", detail="standalone ellipsis"))

        # silent stubs: function/class body reduces to 'pass' or standalone ellipsis
        # heuristic: look for "def" or "class" and then next non-empty, non-comment indented line.
        for i, line in enumerate(lines, start=1):
            m = _RE_DEF_LINE.match(line)
            if not m:
                continue
            kind = m.group(1)
            name = m.group(2)

            # find next meaningful line
            j = i
            while j < len(lines):
                j += 1
                if j > len(lines):
                    break
                nxt = lines[j - 1]
                if nxt.strip() == "" or nxt.lstrip().startswith("#"):
                    continue
                # only consider indented bodies
                if not nxt.startswith(" ") and not nxt.startswith("\t"):
                    break

                stub_line = nxt.strip()

                # exception marker classes are allowed
                if kind == "class" and _RE_CLASS_EXCEPTION.match(line):
                    if stub_line == "pass":
                        # allowed
                        break

                if stub_line == "pass":
                    findings.append(Finding(path=path, line=j, kind="SILENT_STUB_PASS", detail=f"{kind} {name}"))
                if stub_line == "...":
                    findings.append(Finding(path=path, line=j, kind="SILENT_STUB_ELLIPSIS", detail=f"{kind} {name}"))
                break

    ok = len(findings) == 0
    return Result(ok=ok, findings=findings)

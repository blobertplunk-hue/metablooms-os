# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations

import ast
import os
from dataclasses import dataclass
from typing import Dict, List, Optional


SCAN_EXTENSIONS = {".py"}

EXCLUDE_DIR_FRAGMENTS = {
    os.path.join("docs"),
    os.path.join("examples"),
    os.path.join("tests"),
}


@dataclass
class Violation:
    path: str
    code: str
    detail: str
    line: Optional[int] = None


def _is_excluded(path: str) -> bool:
    norm = path.replace("\\", "/")
    for frag in EXCLUDE_DIR_FRAGMENTS:
        frag_norm = frag.replace("\\", "/").strip("/")
        if f"/{frag_norm}/" in f"/{norm}/":
            return True
    return False


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _is_pass_only(body: List[ast.stmt]) -> bool:
    return len(body) == 1 and isinstance(body[0], ast.Pass)


def _is_ellipsis_expr_only(body: List[ast.stmt]) -> bool:
    """Detect handlers whose body is a single Ellipsis expression statement.

    Note: Python treats an expression statement of the Ellipsis literal as a no-op.
    We treat that as swallowed-exception behavior.
    """
    if len(body) != 1:
        return False
    stmt = body[0]
    if not isinstance(stmt, ast.Expr):
        return False
    val = getattr(stmt, "value", None)
    return isinstance(val, ast.Constant) and val.value is Ellipsis


def _handler_type_name(h: ast.ExceptHandler) -> str:
    if h.type is None:
        return "<bare>"
    if isinstance(h.type, ast.Name):
        return h.type.id
    if isinstance(h.type, ast.Attribute):
        return h.type.attr
    return "<complex>"


def _scan_python_ast(path: str, text: str) -> List[Violation]:
    out: List[Violation] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return out

    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        for h in node.handlers:
            if not isinstance(h, ast.ExceptHandler):
                continue
            tname = _handler_type_name(h)
            lineno = getattr(h, "lineno", None)

            # 1) Bare except is a high-risk swallow surface.
            if h.type is None:
                out.append(
                    Violation(
                        path=path,
                        code="BARE_EXCEPT",
                        detail="bare except without specifying exception type",
                        line=lineno,
                    )
                )
                continue

            # 2) pass-only or ellipsis-only handlers swallow errors silently.
            if _is_pass_only(h.body):
                out.append(
                    Violation(
                        path=path,
                        code="EXCEPT_PASS_ONLY",
                        detail=f"except {tname}: pass",
                        line=lineno,
                    )
                )
                continue
            if _is_ellipsis_expr_only(h.body):
                out.append(
                    Violation(
                        path=path,
                        code="EXCEPT_ELLIPSIS_ONLY",
                        detail=f"except {tname}: <ellipsis-expression>",
                        line=lineno,
                    )
                )
                continue

    return out


def validate_repo(root_path: str, mode: str = "WARN") -> Dict:
    violations: List[Violation] = []
    scanned_files = 0

    for root, _, files in os.walk(root_path):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext not in SCAN_EXTENSIONS:
                continue
            path = os.path.join(root, fn)
            if _is_excluded(path):
                continue
            scanned_files += 1
            text = _read_text(path)
            violations.extend(_scan_python_ast(path, text))

    passed = (len(violations) == 0) if mode.upper() == "FAIL" else True

    return {
        "pass": passed,
        "mode": mode.upper(),
        "scanned": {"files": scanned_files},
        "violations": [v.__dict__ for v in violations],
    }

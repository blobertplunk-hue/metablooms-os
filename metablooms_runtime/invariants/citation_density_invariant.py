"""Citation Binding Invariant (P0)

Purpose:
- Prevent 'research' outputs with unbound claims.
- Require a structured claims list and a citation map binding each claim to sources.

Required artifacts when research_required==True or mode==RESEARCH:
- research/claims.json
- research/citation_map.json
- at least one evidence artifact (e.g., research/source_excerpts.md)

Rules:
- claims.json must contain a list under key 'claims'
- citation_map.json must contain a list under key 'bindings'
- Each claim must have at least one binding
- Each binding must contain at least one source entry
- Optional coverage threshold (default 1.0)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set
import json


class CitationFailClosed(RuntimeError):
    """Raised when claims are missing required citation bindings."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise CitationFailClosed(f"Invalid JSON: {path}: {e}") from e


def enforce(context: Dict[str, Any]) -> None:
    if not (context.get("research_required") or str(context.get("mode", "")).upper() == "RESEARCH"):
        return

    repo_root = context.get("repo_root")
    if not repo_root:
        raise CitationFailClosed("repo_root required for citation invariant enforcement")

    root = Path(repo_root)
    claims_p = root / "research" / "claims.json"
    cmap_p = root / "research" / "citation_map.json"

    claims_obj = _load_json(claims_p)
    cmap_obj = _load_json(cmap_p)

    claims = claims_obj.get("claims")
    bindings = cmap_obj.get("bindings")

    if not isinstance(claims, list):
        raise CitationFailClosed("claims.json must contain a list at key 'claims'")
    if not isinstance(bindings, list):
        raise CitationFailClosed("citation_map.json must contain a list at key 'bindings'")

    # Build binding map: claim_id -> list[sources]
    bound: Dict[str, List[Any]] = {}
    for b in bindings:
        if not isinstance(b, dict):
            continue
        cid = b.get("claim_id")
        sources = b.get("sources")
        if cid is None:
            continue
        if isinstance(sources, list):
            bound.setdefault(str(cid), []).extend(sources)
        else:
            bound.setdefault(str(cid), [])

    missing: List[str] = []
    weak: List[str] = []

    for c in claims:
        if not isinstance(c, dict):
            continue
        cid = str(c.get("claim_id", ""))
        if not cid:
            missing.append("<missing_claim_id>")
            continue
        if cid not in bound:
            missing.append(cid)
            continue
        if len(bound.get(cid, [])) < 1:
            weak.append(cid)

    if missing:
        raise CitationFailClosed(f"RESEARCH FAIL-CLOSED — unbound claims (no bindings): {missing}")
    if weak:
        raise CitationFailClosed(f"RESEARCH FAIL-CLOSED — claims missing sources in bindings: {weak}")

    # Coverage ratio check (defaults to 1.0)
    covered = len(claims)
    ratio = covered / max(1, len(claims))
    threshold = float(context.get('citation_coverage_threshold', 1.0))
    if ratio < threshold:
        raise CitationFailClosed(f"RESEARCH FAIL-CLOSED — citation coverage {ratio:.2f} below threshold {threshold:.2f}")

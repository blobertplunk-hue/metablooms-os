"""Research Materializer (P0)

Creates/normalizes research artifacts so subsequent gates can evaluate them.

Guarantees (idempotent):
- Ensures research/claims.json exists with {version: 1, claims: []}
- Ensures research/citation_map.json exists with {version: 1, bindings: []}
- Auto-injects claim.created_ts (UTC epoch seconds) if missing
- Auto-injects claim_id if missing (UUID4)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import json
import time
import uuid


class ResearchMaterializerFailClosed(RuntimeError):
    """Raised when research artifacts cannot be created or normalized."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ResearchMaterializerFailClosed(f"Invalid JSON: {path}: {e}") from e


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def materialize(context: Dict[str, Any]) -> None:
    repo_root = context.get("repo_root")
    if not repo_root:
        raise ResearchMaterializerFailClosed("repo_root required for research materializer")

    root = Path(repo_root)
    claims_p = root / "research" / "claims.json"
    cmap_p = root / "research" / "citation_map.json"

    now = time.time()

    # claims.json
    obj = _load_json(claims_p) if claims_p.exists() else {"version": 1, "claims": []}
    if not isinstance(obj, dict):
        raise ResearchMaterializerFailClosed("claims.json must be an object")
    if "claims" not in obj or not isinstance(obj.get("claims"), list):
        obj["claims"] = []

    changed = False
    for c in obj["claims"]:
        if not isinstance(c, dict):
            continue
        if "claim_id" not in c or not c.get("claim_id"):
            c["claim_id"] = str(uuid.uuid4())
            changed = True
        if "created_ts" not in c:
            c["created_ts"] = now
            changed = True

    if changed or not claims_p.exists():
        _write_json(claims_p, obj)

    # citation_map.json
    if not cmap_p.exists():
        _write_json(
            cmap_p,
            {"version": 1, "turn_id": context.get("turn_id"), "created_utc": now, "bindings": []},
        )
    cmap = _load_json(cmap_p)
    if not isinstance(cmap, dict):
        raise ResearchMaterializerFailClosed("citation_map.json must be an object")
    if "bindings" not in cmap or not isinstance(cmap.get("bindings"), list):
        cmap["bindings"] = []
        _write_json(cmap_p, cmap)

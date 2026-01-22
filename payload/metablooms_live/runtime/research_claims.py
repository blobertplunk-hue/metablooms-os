"""Research claims helper (P0)

Use this helper for claim generation so claim.created_ts is always present.
This module writes to research/claims.json under repo_root.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import json
import time
import uuid


class ClaimsFailClosed(RuntimeError):
    """Raised when claims cannot be read/written."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"version": 1, "claims": []}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ClaimsFailClosed(f"Invalid JSON: {path}: {e}") from e
    if not isinstance(obj, dict):
        raise ClaimsFailClosed("claims.json must be an object")
    if "claims" not in obj or not isinstance(obj.get("claims"), list):
        obj["claims"] = []
    if "version" not in obj:
        obj["version"] = 1
    return obj


def _write(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")


def add_claim(
    repo_root: str,
    text: str,
    *,
    meta: Optional[Dict[str, Any]] = None,
    claim_id: Optional[str] = None,
    created_ts: Optional[float] = None,
) -> str:
    root = Path(repo_root)
    p = root / "research" / "claims.json"
    obj = _load(p)

    cid = claim_id or str(uuid.uuid4())
    ts = created_ts if created_ts is not None else time.time()

    claim: Dict[str, Any] = {"claim_id": cid, "created_ts": ts, "text": text}
    if meta:
        claim["meta"] = meta

    obj["claims"].append(claim)
    _write(p, obj)
    return cid

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, Iterable, List

DATA_REL = Path("data/hanging_threads/threads.ndjson")

def ensure_store(root: Path) -> Path:
    p = root / DATA_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")
    return p

def append_threads(root: Path, records: Iterable[Dict[str, Any]]) -> int:
    p = ensure_store(root)
    n = 0
    with p.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
            n += 1
    return n

def load_open_threads(root: Path, limit: int = 50) -> List[Dict[str, Any]]:
    p = root / DATA_REL
    if not p.exists():
        return []
    out: List[Dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line:
            continue
        try:
            obj=json.loads(line)
        except Exception:
            continue
        if obj.get("status") == "open":
            out.append(obj)
    # stable ordering: most recent first if timestamp present
    out.sort(key=lambda x: x.get("ts_utc",""), reverse=True)
    return out[:limit]

def mark_resolved(root: Path, thread_id: str, resolution_note: str | None = None) -> None:
    """Append-only resolution: write a resolution event record."""
    p = ensure_store(root)
    evt = {
        "thread_id": thread_id,
        "status": "resolved",
        "trigger_text": resolution_note or "resolved",
        "ts_utc": __import__("time").strftime("%Y-%m-%dT%H:%M:%SZ", __import__("time").gmtime()),
        "source": "resolution",
        "evidence": None,
        "references": None
    }
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, sort_keys=True) + "\n")

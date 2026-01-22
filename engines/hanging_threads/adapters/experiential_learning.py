# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List
from ..persistence import append_threads, load_open_threads
from ...experiential_learning.persistence import list_open_cycles

def sync_open_cycles_to_threads(root: Path, source: str = "experiential_learning") -> int:
    """Create/refresh hanging threads for any open experiential learning cycles.
    Never deletes; uses stable thread_id derived from cycle_id.
    """
    open_cycles = list_open_cycles(root, limit=500)
    if not open_cycles:
        return 0

    existing = {t.get("thread_id") for t in load_open_threads(root, limit=5000)}
    to_add: List[Dict[str, Any]] = []
    for c in open_cycles:
        cid = c.get("cycle_id")
        if not cid:
            continue
        thread_id = "ht_" + cid.replace("el_","el")[:12]
        if thread_id in existing:
            continue
        trig = f"Experiential learning cycle still open: {cid} — {(c.get('prompt') or '').strip()}"
        to_add.append({
            "thread_id": thread_id,
            "status": "open",
            "ts_utc": c.get("ts_utc"),
            "source": source,
            "trigger_text": trig,
            "evidence": None,
            "references": [{"kind":"experiential_learning_cycle","id":cid}]
        })

    return append_threads(root, to_add) if to_add else 0

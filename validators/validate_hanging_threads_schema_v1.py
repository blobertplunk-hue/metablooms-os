# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json
from pathlib import Path

REQUIRED = ["thread_id","status","trigger_text","ts_utc","source"]
ALLOWED_STATUS = {"open","resolved","superseded"}

def validate(root: Path):
    store = root / "data" / "hanging_threads" / "threads.ndjson"
    if not store.exists():
        # no data yet is valid
        return {"ok": True, "note": "no_threads_file"}
    bad = 0
    total = 0
    for line in store.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line:
            continue
        total += 1
        try:
            obj=json.loads(line)
        except Exception:
            bad += 1
            continue
        for k in REQUIRED:
            if k not in obj:
                bad += 1
                break
        else:
            if obj.get("status") not in ALLOWED_STATUS:
                bad += 1
    return {"ok": bad==0, "total": total, "bad": bad}

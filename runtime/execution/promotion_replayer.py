# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Promotion Replayer
Replays registry promotions from ledger on boot to ensure canonical consistency.
Fail-closed principles:
- Never invent pipelines
- Skip invalid entries with diagnostics
- Idempotent: safe to run multiple times
"""

import json
from pathlib import Path

MASTER_PATH = Path(__file__).parents[2] / "registry" / "artifact2_rows_pipelines" / "consolidated" / "artifact2_rows_pipelines_master_v1.json"
PROMOTION_LEDGER = Path(__file__).parents[2] / "ledger" / "registry_promotions.jsonl"
DIAG_LOG = Path(__file__).parents[2] / "diagnostics" / "promotion_replay.log"

def _read_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                rows.append({"ok": False, "failure": "INVALID_JSONL_LINE", "raw": line})
    return rows

def _read_master():
    if not MASTER_PATH.exists():
        return None
    return json.loads(MASTER_PATH.read_text(encoding="utf-8"))

def _write_master(data: dict):
    MASTER_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _log(msg: str):
    DIAG_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(DIAG_LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def replay():
    data = _read_master()
    if data is None:
        _log("MASTER_MISSING")
        return {"ok": False, "failure": "MASTER_MISSING"}

    pipelines = data.get("pipelines", [])
    by_id = {p.get("id"): p for p in pipelines if p.get("id")}

    entries = _read_jsonl(PROMOTION_LEDGER)
    applied = 0
    skipped = 0

    for e in entries:
        if not e.get("ok"):
            skipped += 1
            continue
        pid = e.get("pipeline_id")
        secs = e.get("suggested_sections")
        if not pid or not isinstance(secs, list) or not secs:
            skipped += 1
            continue
        p = by_id.get(pid)
        if p is None:
            skipped += 1
            continue
        # idempotent apply
        p["sections"] = secs
        p["sections_source"] = e.get("source", "promotion_replay")
        p["sections_confidence"] = e.get("confidence")
        applied += 1

    _write_master(data)
    _log(f"REPLAY_DONE applied={applied} skipped={skipped}")
    return {"ok": True, "applied": applied, "skipped": skipped}

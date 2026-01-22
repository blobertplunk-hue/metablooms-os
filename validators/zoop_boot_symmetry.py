# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json
from pathlib import Path

def _iter_events(ledger_text: str):
    for ln in ledger_text.splitlines():
        ln = ln.strip()
        if not ln:
            continue
        if ln.endswith('\\n'):
            ln = ln[:-2]
        try:
            yield json.loads(ln)
        except Exception:
            continue

def run():
    ledger = Path(__file__).resolve().parents[1] / "ledger" / "ledger.ndjson"
    events = list(_iter_events(ledger.read_text(encoding="utf-8", errors="replace")))
    zoops = [e for e in events if e.get("event_type") == "ZOOP"]
    boots = [e for e in events if e.get("event_type") == "BOOT"]
    if zoops and not boots:
        raise RuntimeError("ZOOP_BOOT_SYMMETRY_FAIL: ZOOP without BOOT")
    return "ZOOP_BOOT_SYMMETRY_OK"

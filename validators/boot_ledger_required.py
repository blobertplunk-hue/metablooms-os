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
    if not any(e.get("event_type") == "BOOT" for e in events):
        raise RuntimeError("BOOT_LEDGER_REQUIRED: no BOOT event recorded")
    return "BOOT_LEDGER_REQUIRED_OK"

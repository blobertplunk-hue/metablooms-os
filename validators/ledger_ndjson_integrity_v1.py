# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json, re, time, uuid
from pathlib import Path
_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")

def _append(root: Path, evt: dict):
    lp = root/"ledger"/"ledger.ndjson"
    with lp.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, sort_keys=True)+"\n")

def run():
    root = Path(__file__).resolve().parents[1]
    lp = root/"ledger"/"ledger.ndjson"
    if not lp.exists():
        raise RuntimeError("LEDGER_MISSING")
    line_no = 0
    with lp.open("r", encoding="utf-8") as f:
        for line in f:
            line_no += 1
            if not line.strip(): continue
            try:
                evt = json.loads(line)
            except Exception:
                raise RuntimeError(f"LEDGER_BAD_JSON line {line_no}")
            ts = evt.get("ts")
            if not isinstance(ts, str) or not _TS.match(ts):
                raise RuntimeError(f"LEDGER_SCHEMA_BAD_ts line {line_no}")
            if not isinstance(evt.get("event_type"), str) or not evt.get("event_type"):
                raise RuntimeError(f"LEDGER_SCHEMA_BAD_event_type line {line_no}")
            if not isinstance(evt.get("event_id"), str) or not evt.get("event_id"):
                raise RuntimeError(f"LEDGER_SCHEMA_BAD_event_id line {line_no}")
    _append(root, {
        "event_id": str(uuid.uuid4()),
        "event_type": "LEDGER_VERIFY",
        "validator": "LEDGER_NDJSON_INTEGRITY_V1",
        "status": "OK",
        "checked_lines": line_no,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    return "LEDGER_NDJSON_INTEGRITY_OK"

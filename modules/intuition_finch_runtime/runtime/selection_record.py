# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json, datetime, uuid, os, random

def write_selection_record(root_dir: str, env: dict, finch: dict, note: str|None=None):
    ledger_path = os.path.join(root_dir, "ledger", "selection_record.jsonl")
    rec = {
        "selection_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "environment_vector": env,
        "finch_selection": finch,
        "note": note,
    }
    os.makedirs(os.path.dirname(ledger_path), exist_ok=True)
    with open(ledger_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec

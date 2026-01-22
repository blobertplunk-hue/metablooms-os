# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# Phase C Replay Mode
import json, datetime

def run_replay(task_ref, ledger_path):
    record = {
        "ts": datetime.datetime.utcnow().isoformat()+"Z",
        "phase": "REPLAY",
        "task_ref": task_ref,
        "note": "Phase C replay invoked"
    }
    with open(ledger_path, "a") as f:
        f.write(json.dumps(record)+"\n")
    return record

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Ledger Writer
Records auto-accepted patches for audit and reuse.
"""

import json
from pathlib import Path
from datetime import datetime

LEDGER_PATH = Path(__file__).parents[2] / "ledger" / "auto_patch_acceptances.jsonl"

def write_ledger(entry: dict):
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

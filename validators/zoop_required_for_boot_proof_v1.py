# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json
from pathlib import Path

def run():
    root = Path(__file__).resolve().parents[1]
    receipt = root/"ledger"/"zoop_receipt.json"
    ledger = root/"ledger"/"ledger.ndjson"
    if not receipt.exists(): raise RuntimeError("ZOOP_REQUIRED:missing_zoop_receipt")
    if not ledger.exists(): raise RuntimeError("ZOOP_REQUIRED:missing_ledger")
    r = json.loads(receipt.read_text(encoding="utf-8"))
    zoop_id = r.get("zoop_event_id")
    if not zoop_id: raise RuntimeError("ZOOP_REQUIRED:receipt_missing_zoop_event_id")
    found = False
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        evt = json.loads(line)
        if evt.get("event_type")=="ZOOP" and evt.get("event_id")==zoop_id:
            found = True; break
    if not found: raise RuntimeError("ZOOP_REQUIRED:receipt_event_id_not_found_in_ledger")
    return "ZOOP_REQUIRED_FOR_BOOT_PROOF_OK"

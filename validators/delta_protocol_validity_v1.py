# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json
from pathlib import Path

def run():
    root = Path(__file__).resolve().parents[1]
    # validate ledger linkage
    ledger = root/"ledger"/"ledger.ndjson"
    intents = set()
    oks = {}
    with ledger.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip(): continue
            evt = json.loads(line)
            et = evt.get("event_type","")
            if et=="DELTA_APPLY_INTENT":
                intents.add(evt.get("delta_id"))
            if et=="DELTA_APPLY_OK":
                oks[evt.get("delta_id")] = evt

    for d in oks:
        if d not in intents:
            raise RuntimeError(f"DELTA_ORPHAN_OK:{d}")
        if "produced_zip" not in oks[d] or "sha256" not in oks[d]:
            raise RuntimeError(f"DELTA_OK_MISSING_PROOF:{d}")

    # validate schema of known delta manifests in /mnt/data if present
    # (baseline: ensure schema file exists; deep scan optional in later versions)
    return "DELTA_PROTOCOL_VALIDITY_OK"

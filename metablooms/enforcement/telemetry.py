"""
Telemetry wrapper for SEE / MMD / ECL.
Records why enforcement blocks occurred.
"""
import json, time, pathlib

LEDGER = pathlib.Path("metablooms/LEDGERS/ENFORCEMENT_TELEMETRY.jsonl")

def log(event, detail):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts":time.time(),"event":event,"detail":detail})+"\n")

def see_violation(detail): log("SEE_BLOCK", detail)
def mmd_violation(detail): log("MMD_BLOCK", detail)
def ecl_violation(detail): log("ECL_BLOCK", detail)

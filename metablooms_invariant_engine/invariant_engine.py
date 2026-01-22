# MetaBlooms Invariant Engine (IE) — Stub
from dataclasses import dataclass
from typing import List, Dict, Optional
import json, time
from pathlib import Path

LEDGER_PATH = "/mnt/data/book_report/invariant_ledger.jsonl"

@dataclass
class Proposal:
    proposal_id: str
    source: str
    statement: str
    scope: str
    evidence_paths: List[str]
    requested_by: str

def append_ledger(entry: Dict):
    Path(LEDGER_PATH).parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def ratify(proposal: Proposal):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "action": "RATIFIED",
        "proposal_id": proposal.proposal_id
    }
    append_ledger(entry)

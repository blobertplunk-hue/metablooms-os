# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json, uuid, hashlib
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def ensure_ledger(ledger_path: Path) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    if not ledger_path.exists():
        ledger_path.write_text("", encoding="utf-8")

def append_event(ledger_path: Path, evt: Dict[str, Any]) -> None:
    ensure_ledger(ledger_path)
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evt, sort_keys=True, ensure_ascii=False) + "\n")

def event_id() -> str:
    return str(uuid.uuid4())

def tail_sha256(ledger_path: Path, n_lines: int = 50) -> str:
    if not ledger_path.exists():
        return ""
    lines = ledger_path.read_text(encoding="utf-8").splitlines()
    tail = "\n".join(lines[-n_lines:]).encode("utf-8")
    return hashlib.sha256(tail).hexdigest()

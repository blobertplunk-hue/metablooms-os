"""Append-only ledger writers (P0)

Guarantees:
- Creates directories if missing
- Appends JSON lines (jsonl) only; never overwrites existing entries
- Provides deterministic minimal schema for auditability
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_chat_ledger(repo_root: str, entry: Dict[str, Any]) -> Path:
    """Write one append-only chat ledger entry."""
    p = Path(repo_root) / "ledgers" / "chat_ledger.jsonl"
    entry = dict(entry)
    entry.setdefault("ts_utc", time.time())
    entry.setdefault("ledger", "chat")
    _append_jsonl(p, entry)
    return p


def write_project_ledger(repo_root: str, entry: Dict[str, Any]) -> Path:
    """Write one append-only project ledger entry."""
    p = Path(repo_root) / "ledgers" / "project_ledger.jsonl"
    entry = dict(entry)
    entry.setdefault("ts_utc", time.time())
    entry.setdefault("ledger", "project")
    _append_jsonl(p, entry)
    return p

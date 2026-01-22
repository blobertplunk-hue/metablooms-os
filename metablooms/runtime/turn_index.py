from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

class TurnIndexError(RuntimeError):
    pass

def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def discover_latest_boot_receipt(os_root: Path) -> Path | None:
    turns = os_root / "ledgers" / "turns"
    if not turns.exists():
        return None
    receipts = []
    for d in turns.iterdir():
        r = d / "boot_receipt.json"
        if d.is_dir() and r.exists():
            receipts.append(r)
    if not receipts:
        return None
    receipts.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return receipts[0]

def allocate_turn_index(os_root: Path, turn_id: str, allow_initial: bool = False) -> int:
    latest = discover_latest_boot_receipt(os_root)
    if latest is None:
        if not allow_initial:
            raise TurnIndexError("NO_PRIOR_BOOT_RECEIPT_FOR_INDEX")
        idx = 0
    else:
        prior = _read_json(latest)
        idx = int(prior.get("turn_index", -1)) + 1
        if idx <= 0:
            idx = 1
    out_dir = os_root / "ledgers" / "turns" / turn_id
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {
        "receipt_type": "TURN_INDEX_RECEIPT",
        "turn_id": turn_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "turn_index": idx
    }
    (out_dir / "turn_index_receipt.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
    return idx

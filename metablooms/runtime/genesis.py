from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

def ensure_genesis_receipt(os_root: Path, turn_id: str) -> Path:
    out = os_root / "ledgers" / "genesis"
    out.mkdir(parents=True, exist_ok=True)
    p = out / "GENESIS_BOOT_RECEIPT.json"
    if p.exists():
        return p
    obj = {
        "receipt_type": "GENESIS_BOOT_RECEIPT",
        "turn_id": turn_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "policy": "INITIAL_BOOT_EXCEPTION"
    }
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return p

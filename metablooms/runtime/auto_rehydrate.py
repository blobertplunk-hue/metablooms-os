from __future__ import annotations
from pathlib import Path
import json
from datetime import datetime

class RehydrateError(RuntimeError):
    pass

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def discover_latest_turn_dir(os_root: Path) -> Path | None:
    turns = os_root / "ledgers" / "turns"
    if not turns.exists():
        return None
    dirs = []
    for d in turns.iterdir():
        if d.is_dir() and (d / "boot_receipt.json").exists():
            dirs.append(d)
    if not dirs:
        return None
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return dirs[0]

def auto_rehydrate(os_root: Path, turn_id: str) -> dict:
    # P0: verify latest snapshot integrity (if any) before rehydration
    try:
        from metablooms.runtime.snapshot_verify import find_latest_snapshot, verify_snapshot_file
        snap = find_latest_snapshot(os_root)
        if snap is not None:
            verify_snapshot_file(snap)
    except Exception as _e:
        raise RehydrateError(f"SNAPSHOT_VERIFY_FAILED:{_e}")

    """
    Auto-rehydrate must be invoked BEFORE any other logic.
    Evidence: writes ledgers/turns/<TURN_ID>/rehydrate_receipt.json
    Fail-closed: raises RehydrateError if no prior receipt exists.
    """
    latest_turn_dir = discover_latest_turn_dir(os_root)
    if latest_turn_dir is None:
        raise RehydrateError("NO_PRIOR_TURN_RECEIPT_FOUND")

    prior_receipt = _load_json(latest_turn_dir / "boot_receipt.json")

    out_dir = os_root / "ledgers" / "turns" / turn_id
    out_dir.mkdir(parents=True, exist_ok=True)

    rehydrate_receipt = {
        "receipt_type": "TURN_REHYDRATE_RECEIPT",
        "turn_id": turn_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "rehydrated_from_turn": prior_receipt.get("turn_id", "UNKNOWN"),
        "rehydrated_from_path": str(latest_turn_dir / "boot_receipt.json"),
        "rehydrate_ok": True,
        "state_mode": "REHYDRATED"
    }
    (out_dir / "rehydrate_receipt.json").write_text(json.dumps(rehydrate_receipt, indent=2), encoding="utf-8")
    return rehydrate_receipt

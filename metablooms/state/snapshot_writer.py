
from pathlib import Path
import json, hashlib
from datetime import datetime

def write_snapshot(os_root: Path, turn_id: str, materialized_state: dict) -> Path:
    snaps = os_root / "metablooms" / "state" / "snapshots"
    snaps.mkdir(parents=True, exist_ok=True)
    payload = {
        "snapshot_type": "STATE_SNAPSHOT",
        "turn_id": turn_id,
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "state": materialized_state
    }
    raw = json.dumps(payload, sort_keys=True).encode("utf-8")
    sha = hashlib.sha256(raw).hexdigest()
    payload["sha256"] = sha
    out = snaps / f"SNAPSHOT_TURN_{turn_id}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out

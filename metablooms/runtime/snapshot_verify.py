from __future__ import annotations
from pathlib import Path
import json, hashlib

class SnapshotVerifyError(RuntimeError):
    pass

def _hash_dict(d: dict) -> str:
    raw = json.dumps(d, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def verify_snapshot_file(snapshot_path: Path) -> None:
    obj = json.loads(snapshot_path.read_text(encoding="utf-8"))
    expected = obj.get("sha256")
    if not expected:
        raise SnapshotVerifyError("SNAPSHOT_SHA256_MISSING")
    # recompute without trusting stored sha256 field
    recompute_obj = dict(obj)
    recompute_obj.pop("sha256", None)
    actual = _hash_dict(recompute_obj)
    if actual != expected:
        raise SnapshotVerifyError("SNAPSHOT_SHA256_MISMATCH")

def find_latest_snapshot(os_root: Path) -> Path | None:
    snaps = os_root / "metablooms" / "state" / "snapshots"
    if not snaps.exists():
        return None
    files = [p for p in snaps.iterdir() if p.is_file() and p.name.startswith("SNAPSHOT_TURN_") and p.suffix == ".json"]
    if not files:
        return None
    files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0]

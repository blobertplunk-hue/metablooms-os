from __future__ import annotations
from pathlib import Path
import json, os, time, socket
from datetime import datetime

class TurnLockError(RuntimeError):
    pass

def _utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        # Works on Unix-like. If not permitted, treat as alive to fail-safe.
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return True

def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def acquire_turn_lock(os_root: Path, turn_id: str, stale_after_s: int = 900) -> Path:
    """
    Crash-safe single-writer lock.
    - If lock exists and is fresh AND pid is alive -> fail (concurrent)
    - If lock exists but stale OR pid dead -> reclaim, writing a recovery receipt
    """
    ledgers = os_root / "ledgers"
    ledgers.mkdir(parents=True, exist_ok=True)
    lock_path = ledgers / "TURN_LOCK.json"

    now = time.time()
    this = {
        "turn_id": turn_id,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "created_utc": _utc_now(),
        "created_unix": now
    }

    if lock_path.exists():
        try:
            prior = _read_json(lock_path)
            prior_pid = int(prior.get("pid", -1))
            prior_created = float(prior.get("created_unix", 0.0))
            age = max(0.0, now - prior_created)
            alive = _pid_alive(prior_pid)

            if alive and age <= stale_after_s:
                raise TurnLockError("P0_FAIL: CONCURRENT_TURN_DETECTED (lock fresh + pid alive)")

            # Reclaim lock (stale or pid dead) with explicit recovery receipt
            rec_dir = os_root / "ledgers" / "turns" / turn_id
            rec_dir.mkdir(parents=True, exist_ok=True)
            recovery = {
                "receipt_type": "TURN_LOCK_RECOVERY_RECEIPT",
                "turn_id": turn_id,
                "timestamp_utc": _utc_now(),
                "recovered_from": prior,
                "recovery_reason": ("PID_DEAD" if not alive else "STALE_LOCK"),
                "stale_after_s": stale_after_s,
                "prior_lock_age_s": age
            }
            (rec_dir / "turn_lock_recovery_receipt.json").write_text(json.dumps(recovery, indent=2), encoding="utf-8")
        except TurnLockError:
            raise
        except Exception as e:
            raise TurnLockError(f"P0_FAIL: TURN_LOCK_UNREADABLE_OR_INVALID: {e}")

    lock_path.write_text(json.dumps(this, indent=2), encoding="utf-8")
    return lock_path

def release_turn_lock(os_root: Path, turn_id: str) -> None:
    lock_path = os_root / "ledgers" / "TURN_LOCK.json"
    if not lock_path.exists():
        return
    try:
        prior = _read_json(lock_path)
        if prior.get("turn_id") != turn_id:
            # Do not remove someone else's lock
            return
    except Exception:
        return
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass

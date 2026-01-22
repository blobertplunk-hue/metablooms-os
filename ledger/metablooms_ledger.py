# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms append-only ledger (NDJSON) with hash chaining.

Purpose:
  - Provide a mechanically-enforced bridge between 'what happened' and on-disk evidence.
  - Make regressions and substitutions visible through immutable event history.

Design constraints:
  - Single file append (ledger.ndjson) to keep it durable and simple.
  - Each line is a canonical JSON object with 'hash' chained via 'prev_hash'.
  - No external dependencies; safe to run in restricted Python environments.
"""

from __future__ import annotations

import json
import os
import time
import uuid
import hashlib
from dataclasses import dataclass
from typing import Any, Dict, Optional

GENESIS = "GENESIS"

def _utc_iso() -> str:
    # UTC timestamp with 'Z'
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _canonical_json(obj: Dict[str, Any]) -> bytes:
    # Stable ordering + no whitespace so hashing is deterministic.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def _compute_event_hash(event: Dict[str, Any]) -> str:
    tmp = dict(event)
    tmp["hash"] = ""
    return _sha256_bytes(_canonical_json(tmp))

def _read_last_hash(path: str) -> str:
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return GENESIS
    # Read last non-empty line without loading entire file.
    with open(path, "rb") as f:
        f.seek(0, os.SEEK_END)
        end = f.tell()
        # Scan backwards for newline.
        offset = min(4096, end)
        f.seek(-offset, os.SEEK_END)
        chunk = f.read(offset)
    lines = [ln for ln in chunk.splitlines() if ln.strip()]
    if not lines:
        return GENESIS
    try:
        last = json.loads(lines[-1].decode("utf-8"))
        return str(last.get("hash") or GENESIS)
    except Exception:
        # If corrupted tail, fail-closed by indicating unknown prior hash.
        return "CORRUPT_TAIL"

@dataclass
class LedgerWriter:
    ledger_path: str
    run_id: str
    actor_default: str = "MetaBlooms"

    def append(self, event_type: str, payload: Dict[str, Any], severity: str = "INFO", actor: Optional[str] = None) -> Dict[str, Any]:
        prev_hash = _read_last_hash(self.ledger_path)
        evt = {
            "ts": _utc_iso(),
            "event_id": str(uuid.uuid4()),
            "run_id": self.run_id,
            "event_type": event_type,
            "severity": severity,
            "actor": actor or self.actor_default,
            "payload": payload,
            "prev_hash": prev_hash,
            "hash": "",
        }
        evt["hash"] = _compute_event_hash(evt)

        line = _canonical_json(evt) + b"\n"

        # Append atomically and fsync to reduce loss on crash.
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        with open(self.ledger_path, "ab") as f:
            f.write(line)
            f.flush()
            try:
                os.fsync(f.fileno())
            except OSError:
                # Some environments may not support fsync; best-effort.
                pass

        return evt

def init_ledger(root_dir: str, run_id: Optional[str] = None, actor_default: str = "MetaBlooms") -> LedgerWriter:
    rid = run_id or str(uuid.uuid4())
    ledger_path = os.path.join(root_dir, "ledger", "ledger.ndjson")
    return LedgerWriter(ledger_path=ledger_path, run_id=rid, actor_default=actor_default)

def verify_ledger_chain(ledger_path: str, max_lines: int = 50000) -> Dict[str, Any]:
    """Verify hash chaining integrity. Returns a small report.

    Fail-closed expectation:
      - If any line is malformed or hash chain breaks, ok=False.
    """
    if not os.path.exists(ledger_path):
        return {"ok": False, "reason": "MISSING_LEDGER", "checked": 0}

    checked = 0
    prev = GENESIS
    with open(ledger_path, "rb") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            checked += 1
            if checked > max_lines:
                return {"ok": False, "reason": "MAX_LINES_EXCEEDED", "checked": checked}
            try:
                evt = json.loads(raw.decode("utf-8"))
            except Exception:
                return {"ok": False, "reason": "MALFORMED_JSON", "checked": checked}

            if str(evt.get("prev_hash")) != prev:
                return {"ok": False, "reason": "CHAIN_BROKEN", "checked": checked, "expected_prev": prev, "found_prev": evt.get("prev_hash")}
            expected_hash = _compute_event_hash(evt)
            if str(evt.get("hash")) != expected_hash:
                return {"ok": False, "reason": "HASH_MISMATCH", "checked": checked}
            prev = str(evt.get("hash"))

    return {"ok": True, "checked": checked, "tail_hash": prev}

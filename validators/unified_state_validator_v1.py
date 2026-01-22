# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""validators/unified_state_validator_v1.py
Unified state validator: ensures core SSOT state files exist after boot.
Fail-closed unless MB_ALLOW_LEGACY_VALIDATION=1.
"""
from __future__ import annotations
import json, os
from pathlib import Path

def validate(root: Path) -> dict:
    allow_legacy = os.environ.get("MB_ALLOW_LEGACY_VALIDATION","0") == "1"
    rc_path = root / "runtime" / "RUN_CONTEXT.json"
    if not rc_path.exists():
        if allow_legacy:
            return {"ok": True, "legacy": True, "missing": "runtime/RUN_CONTEXT.json"}
        raise FileNotFoundError("MISSING_REQUIRED_STATE: runtime/RUN_CONTEXT.json")

    # basic JSON validity
    try:
        ctx = json.loads(rc_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"RUN_CONTEXT_INVALID_JSON: {e}")

    # minimal required keys
    required_keys = ["run_id","state","state_history","created_utc"]
    missing = [k for k in required_keys if k not in ctx]
    if missing:
        raise RuntimeError(f"RUN_CONTEXT_MISSING_KEYS: {missing}")

    # ledger must exist and be non-empty
    ledger_path = root / "ledger" / "ledger.ndjson"
    if not ledger_path.exists():
        if allow_legacy:
            return {"ok": True, "legacy": True, "missing": "ledger/ledger.ndjson"}
        raise FileNotFoundError("MISSING_REQUIRED_STATE: ledger/ledger.ndjson")
    if ledger_path.stat().st_size == 0:
        raise RuntimeError("LEDGER_EMPTY")

    return {"ok": True, "legacy": False}

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(validate(root))

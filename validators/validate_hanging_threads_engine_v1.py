# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json
from pathlib import Path

REQUIRED = ["thread_id","status","trigger_text","ts_utc","source"]
ALLOWED_STATUS = {"open","resolved","superseded"}

def validate(root: Path):
    # engine files exist
    engine_dir = root / "engines" / "hanging_threads"
    required_files = [
        engine_dir / "boot_hook.py",
        engine_dir / "persistence.py",
        engine_dir / "detector.py",
        engine_dir / "schemas" / "hanging_thread.schema.json",
    ]
    for p in required_files:
        if not p.exists():
            return {"ok": False, "error": f"missing_required_file:{p.as_posix()}"}
    return {"ok": True}

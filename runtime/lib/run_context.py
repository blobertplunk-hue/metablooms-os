# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json, uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# RUN_CONTEXT_RELOCATION_SAFE_v1
from pathlib import Path
import os as _os

def _os_root_from_here() -> Path:
    # run_context.py is at .../MetaBlooms_OS/runtime/lib/run_context.py
    # parents[2] => MetaBlooms_OS
    return Path(__file__).resolve().parents[2]

def _default_run_root() -> Path:
    # Prefer explicit env var, else a writable directory within the OS bundle
    env = _os.environ.get("METABLOOMS_RUN_ROOT")
    if env:
        return Path(env).expanduser().resolve()
    return _os_root_from_here() / "runtime" / ".run"

def _ensure_run_root(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


ENGINE_STATES = ["IDLE","VALIDATING_INPUTS","RUNNING","VALIDATING_OUTPUTS","LEDGERING","DONE","FAILED"]

def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def create_run_context(root: Path, engine_name: str, engine_version: str, inputs: List[Dict[str, Any]]) -> Dict[str, Any]:
    rt = _default_run_root()

    ensure_dir(rt)
    ctx = {
        "run_id": str(uuid.uuid4()),
        "engine_name": engine_name,
        "engine_version": engine_version,
        "inputs": inputs,
        "state": "IDLE",
        "state_history": [{"state": "IDLE", "ts": utc_now(), "message": "created"}],
        "outputs": [],
        "failures": [],
        "created_utc": utc_now(),
    }
    (rt / "RUN_CONTEXT.json").write_text(json.dumps(ctx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return ctx

def load_run_context(root: Path) -> Dict[str, Any]:
    return json.loads((rt / "RUN_CONTEXT.json").read_text(encoding="utf-8"))

def save_run_context(root, ctx) -> None:
    """Persist run context to runtime/.run/RUN_CONTEXT.json (relocation-safe)."""
    rr = _ensure_run_root(_default_run_root())
    (rr / "RUN_CONTEXT.json").write_text(json.dumps(ctx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def transition(ctx: Dict[str, Any], new_state: str, message: str = "") -> None:
    if new_state not in ENGINE_STATES:
        raise ValueError(f"Invalid state: {new_state}")
    ctx["state"] = new_state
    ctx["state_history"].append({"state": new_state, "ts": utc_now(), "message": message})

def record_output(ctx: Dict[str, Any], path: str, sha256: str | None = None) -> None:
    ctx["outputs"].append({"path": path, "sha256": sha256})

def record_failure(ctx: Dict[str, Any], failure: Dict[str, Any]) -> None:
    ctx["failures"].append(failure)



# === GOVERNANCE FIX: defer runtime side-effects until post-boot ===
BOOT_COMPLETED = False

def activate_run_context(base_dir=None):
    """Initialize run context AFTER BOOT_OK."""
    global BOOT_COMPLETED
    BOOT_COMPLETED = True
    try:
        from pathlib import Path
        root = Path(base_dir) if base_dir else Path.cwd()
        run_dir = root / "runtime" / "runs"
        run_dir.mkdir(parents=True, exist_ok=True)
        meta = run_dir / "run_context.ready"
        meta.write_text("OK", encoding="utf-8")
        return run_dir
    except Exception as e:
        raise RuntimeError(f"activate_run_context failed: {e}")

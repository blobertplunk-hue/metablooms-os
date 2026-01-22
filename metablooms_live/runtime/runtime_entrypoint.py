"""Mandatory Runtime Entrypoint (P0)

All CODE/DEBUG/RESEARCH work should execute through this entrypoint in order to:
- enforce preflight/postflight gates
- emit minimal telemetry for auditability

This module provides a small runtime harness. It does not claim integration with
external UI automation; it is a local, file-backed runner.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional
import hashlib
import json


class RuntimeFailClosed(RuntimeError):
    """Raised when runtime invariants block execution/commit."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def _telemetry_dir(repo_root: str) -> Path:
    tdir = Path(repo_root) / "telemetry"
    tdir.mkdir(parents=True, exist_ok=True)
    return tdir


def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(path.read_text(encoding="utf-8") + json.dumps(obj) + "\n", encoding="utf-8") if path.exists() else path.write_text(json.dumps(obj) + "\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class RuntimeResult:
    ok: bool
    turn_id: str
    commit: bool
    repo_root: str


def run_runtime(
    repo_root: str,
    *,
    turn_id: str,
    commit: bool = False,
    allow_open_expectations: bool = False,
    work: Optional[Callable[[], Any]] = None,
) -> RuntimeResult:
    """Run a minimal runtime session with telemetry and optional callback."""
    if not repo_root:
        raise RuntimeFailClosed("repo_root required")

    root = Path(repo_root)

    # Optional invariant: open expectations block commit unless explicitly allowed.
    open_expectations = root / "expectations" / "OPEN_EXPECTATIONS.json"
    if commit and open_expectations.exists() and not allow_open_expectations:
        raise RuntimeFailClosed(
            "Open expectations present; commit blocked (set allow_open_expectations=True to override)"
        )

    tdir = _telemetry_dir(repo_root)
    events_p = tdir / "events.jsonl"
    hashes_p = tdir / "hashes.jsonl"
    prov_p = tdir / "provenance.jsonl"

    ts = datetime.now(timezone.utc).isoformat()
    _append_jsonl(events_p, {"turn_id": turn_id, "event": "START", "ts": ts})

    # Record hashes of key entrypoints if present
    for rel in ("BOOT_METABLOOMS.py", "RUN_METABLOOMS.py"):
        p = root / rel
        if p.exists():
            _append_jsonl(hashes_p, {"turn_id": turn_id, "ts": ts, "path": rel, "sha256": _sha256(p)})

    # Execute work callback
    if work is not None:
        work()

    if commit:
        _append_jsonl(prov_p, {"turn_id": turn_id, "ts": ts, "commit": True})

    _append_jsonl(events_p, {"turn_id": turn_id, "event": "END", "ts": datetime.now(timezone.utc).isoformat()})

    return RuntimeResult(ok=True, turn_id=turn_id, commit=commit, repo_root=repo_root)

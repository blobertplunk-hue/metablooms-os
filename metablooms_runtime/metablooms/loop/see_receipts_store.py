"""SEE receipt storage utilities.

Phase: 2 (iteration accounting)

Responsibilities:
- Create a run directory for a SEE loop.
- Write per-iteration receipts as JSON.
- Write a loop-level receipt as JSON.
- Maintain a manifest with sha256 hashes for all receipt files.

This module is intentionally stdlib-only.
"""

from __future__ import annotations

import json
import os
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from metablooms.schemas.see_receipt import SEEIterationReceipt, SEELoopReceipt


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def init_loop_run(output_root: str, task_id: str) -> Tuple[str, str, str]:
    """Create a loop run directory and return (loop_id, loop_dir, started_utc)."""
    started_utc = _utc_now_iso()
    loop_id = f"see_{task_id}_{started_utc.replace(':','').replace('-','')}"
    loop_dir = os.path.join(output_root, loop_id)
    ensure_dir(loop_dir)
    ensure_dir(os.path.join(loop_dir, "iterations"))
    return loop_id, loop_dir, started_utc


def write_iteration_receipt(loop_dir: str, receipt: SEEIterationReceipt) -> str:
    """Write an iteration receipt JSON; return relative path within loop dir."""
    rel = os.path.join("iterations", f"iter_{receipt.iteration:03d}.json")
    abs_path = os.path.join(loop_dir, rel)
    ensure_dir(os.path.dirname(abs_path))
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(receipt.to_dict(), f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return rel


def write_loop_receipt(loop_dir: str, receipt: SEELoopReceipt) -> str:
    rel = "loop_receipt.json"
    abs_path = os.path.join(loop_dir, rel)
    with open(abs_path, "w", encoding="utf-8") as f:
        json.dump(receipt.to_dict(), f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
    return rel


def write_manifest(loop_dir: str) -> str:
    """Hash all json receipts under loop_dir and write manifest.json."""
    manifest: Dict[str, Any] = {
        "generated_utc": _utc_now_iso(),
        "files": [],
    }

    for root, _dirs, files in os.walk(loop_dir):
        for name in files:
            if not name.endswith(".json"):
                continue
            abs_path = os.path.join(root, name)
            rel_path = os.path.relpath(abs_path, loop_dir)
            manifest["files"].append(
                {
                    "path": rel_path.replace("\\", "/"),
                    "sha256": _sha256_file(abs_path),
                }
            )

    manifest["files"] = sorted(manifest["files"], key=lambda x: x["path"])

    out = os.path.join(loop_dir, "manifest.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")

    return "manifest.json"


def utc_now_iso() -> str:
    return _utc_now_iso()

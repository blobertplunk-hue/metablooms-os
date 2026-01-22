"""Minimal telemetry writer (P0)

This supports the 'heuristic vs MetaBlooms' comparison telemetry the user expects.
It is append-only (ndjson).

Files:
- telemetry/heuristic_vs_metablooms.ndjson
- telemetry/telemetry_index.json (lightweight manifest)
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict


def _append_ndjson(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(obj, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def write_hvm_event(repo_root: str, event: Dict[str, Any]) -> Path:
    p = Path(repo_root) / "telemetry" / "heuristic_vs_metablooms.ndjson"
    event = dict(event)
    event.setdefault("ts_utc", time.time())
    event.setdefault("stream", "heuristic_vs_metablooms")
    _append_ndjson(p, event)
    return p


def upsert_index(repo_root: str) -> Path:
    root = Path(repo_root)
    idx = root / "telemetry" / "telemetry_index.json"
    idx.parent.mkdir(parents=True, exist_ok=True)

    def _count_lines(p: Path) -> int:
        if not p.exists():
            return 0
        with p.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)

    hvm = root / "telemetry" / "heuristic_vs_metablooms.ndjson"
    logs = root / "telemetry" / "logs.ndjson"

    obj = {
        "updated_utc": time.time(),
        "files": {
            "heuristic_vs_metablooms": str(hvm.relative_to(root)) if hvm.exists() else "telemetry/heuristic_vs_metablooms.ndjson",
            "logs": str(logs.relative_to(root)) if logs.exists() else "telemetry/logs.ndjson"
        },
        "counts": {
            "heuristic_vs_metablooms_events": _count_lines(hvm),
            "log_events": _count_lines(logs)
        }
    }
    idx.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return idx

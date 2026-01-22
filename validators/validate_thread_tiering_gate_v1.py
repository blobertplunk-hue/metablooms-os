# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# validate_thread_tiering_gate_v1.py
"""
THREAD_TIERING_GATE_V1 (fail-closed)

Purpose:
- Treat Hanging Threads as stateful objects (transactional), not ad hoc notes.
- Enforce Tiering integrity and *block progress* if any Tier-3 threads are unresolved.

This gate is intentionally conservative and deterministic:
- It does not infer tier from text.
- It validates the thread record schema and enforces explicit, auditable states.
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime

ALLOWED_TIERS = {1, 2, 3}

# Statuses are intentionally small; you can extend later, but do so explicitly.
OPEN_STATUSES = {"open", "blocked", "in_progress"}
CLOSED_STATUSES = {"resolved", "tied_off", "closed", "done", "archived"}

REQUIRED_FIELDS = {
    "thread_id": str,
    "transaction_id": str,
    "tier": int,
    "status": str,
    "summary": str,
    "created_utc": str,
}

OPTIONAL_FIELDS = {
    "roi_score": (int, float),
    "confidence": (int, float),
    "tags": list,
    "source_refs": list,
    "contradicts": list,
    "last_updated_utc": str,
    "compensation": dict,
}

def _load_ndjson(p: Path) -> list[dict]:
    if not p.exists():
        return []
    out = []
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception as e:
            raise RuntimeError(f"THREAD_TIERING_GATE_V1: invalid JSON on line {i} in {p.as_posix()}: {e}")
    return out

def _assert_schema(t: dict, idx: int, source: str) -> None:
    for k, typ in REQUIRED_FIELDS.items():
        if k not in t:
            raise RuntimeError(f"THREAD_TIERING_GATE_V1: missing required field '{k}' (idx={idx}, source={source})")
        if not isinstance(t[k], typ):
            raise RuntimeError(f"THREAD_TIERING_GATE_V1: wrong type for '{k}' (idx={idx}, source={source}, got={type(t[k]).__name__})")
        if typ is str and not str(t[k]).strip():
            raise RuntimeError(f"THREAD_TIERING_GATE_V1: empty '{k}' (idx={idx}, source={source})")

    tier = t.get("tier")
    if tier not in ALLOWED_TIERS:
        raise RuntimeError(f"THREAD_TIERING_GATE_V1: invalid tier {tier!r} (idx={idx}, source={source}); allowed={sorted(ALLOWED_TIERS)}")

    status = str(t.get("status")).strip()
    if status not in (OPEN_STATUSES | CLOSED_STATUSES):
        raise RuntimeError(
            f"THREAD_TIERING_GATE_V1: invalid status {status!r} (idx={idx}, source={source}); "
            f"open={sorted(OPEN_STATUSES)} closed={sorted(CLOSED_STATUSES)}"
        )

    # Optional fields type checks (if present)
    for k, typ in OPTIONAL_FIELDS.items():
        if k in t and t[k] is not None and not isinstance(t[k], typ):
            raise RuntimeError(f"THREAD_TIERING_GATE_V1: wrong type for optional '{k}' (idx={idx}, source={source}, got={type(t[k]).__name__})")

def _find_thread_store(root: Path) -> list[Path]:
    # Prefer canonical threads store; keep backward compat.
    candidates = [
        root / "threads" / "threads.ndjson",
        root / "data" / "hanging_threads" / "threads.ndjson",
    ]
    return [p for p in candidates if p.exists()]

def run(root: Path, *, strict: bool = True) -> dict:
    stores = _find_thread_store(root)
    # If no store exists, treat as empty but record.
    all_threads: list[tuple[str, dict]] = []
    if stores:
        for sp in stores:
            for t in _load_ndjson(sp):
                all_threads.append((sp.as_posix(), t))

    # Validate schema
    for idx, (source, t) in enumerate(all_threads, start=1):
        _assert_schema(t, idx, source)

    # Block unresolved Tier-3
    tier3_open = []
    for source, t in all_threads:
        if int(t.get("tier")) == 3 and str(t.get("status")).strip() in OPEN_STATUSES:
            tier3_open.append({"source": source, "thread_id": t.get("thread_id"), "transaction_id": t.get("transaction_id"), "status": t.get("status"), "summary": t.get("summary")})

    if tier3_open:
        # fail-closed: this is a hard block
        raise RuntimeError(
            "TIER3_THREADS_PRESENT: Unresolved Tier-3 threads block progress. "
            f"count={len(tier3_open)}; examples={tier3_open[:5]}"
        )

    return {
        "ok": True,
        "validator": "THREAD_TIERING_GATE_V1",
        "stores": [p.as_posix() for p in stores],
        "thread_count": len(all_threads),
        "tier3_open_count": 0,
        "ts": datetime.utcnow().isoformat() + "Z",
    }


# Back-compat for validator_runner_v1.py

def validate(root: Path):
    return run(root)

# ECL_VERSION: 1
# ECL_SCOPE: METABLOOMS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""Decision Trace helper (governed, v1).

This module provides a small, stable API to write *sanitized* decision records
into the append-only JSONL ledger.

It is explicitly NOT a chain-of-thought exporter.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional


def _utc_iso() -> str:
    # Use epoch -> gmtime -> ISO-ish string without depending on datetime tz plumbing
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def get_ledger_path(root: str) -> str:
    return os.path.join(root, "metablooms", "governance", "DECISION_TRACE_APPEND_ONLY.jsonl")


def record_decision(
    root: str,
    objective_key: str,
    decision_id: str,
    decision: str,
    rationale: List[str],
    assumptions: List[str],
    failure_surfaces: List[str],
    evidence_refs: Optional[List[str]] = None,
    actor: str = "assistant",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Append a sanitized decision record to the JSONL ledger.

    Parameters are intentionally explicit and structured.
    """

    rec: Dict[str, Any] = {
        "ts_utc": _utc_iso(),
        "objective_key": objective_key,
        "decision_id": decision_id,
        "decision": decision,
        "rationale": list(rationale),
        "assumptions": list(assumptions),
        "failure_surfaces": list(failure_surfaces),
        "evidence_refs": list(evidence_refs or []),
        "actor": actor,
    }

    if extra:
        # Ensure JSON-serializable best-effort; callers should keep extra small.
        rec["extra"] = extra

    ledger = get_ledger_path(root)
    os.makedirs(os.path.dirname(ledger), exist_ok=True)

    # Append-only write.
    with open(ledger, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    return rec

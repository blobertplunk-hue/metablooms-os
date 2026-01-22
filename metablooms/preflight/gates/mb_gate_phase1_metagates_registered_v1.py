# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: P0.PHASE1.METAGATES.REGISTERED (v1)

Purpose
- Phase 1 baseline requires that the Phase 1 metagates are byte-present and registered.

Notes
- This OS uses a preflight gate chain (metablooms/preflight/preflight_gate_chain_v1.json).
- A dedicated metagate registry is introduced here as a first-class registry at
  metablooms/registry/metagate_registry_v1.json.

Fail-closed
- If the registry is missing, unparseable, or required metagates are absent, this gate fails.
"""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Dict, Optional


GATE_ID = "GATE.P0.PHASE1.METAGATES.REGISTERED.V1"
P0 = True
REG_REL = os.path.join("metablooms", "registry", "metagate_registry_v1.json")

REQUIRED = [
    "METAGATE.P0.PROJECT_FILES.MATERIALIZE_FIRST.V1",
    "METAGATE.P0.ZROOT.SENTINEL.MATCH.V1",
    "METAGATE.P0.NO_PARALLEL_ARCHIVE_WITHOUT_STATE_RECONCILE.V1",
    "METAGATE.P0.ARCHIVE.SINGLE_WRITER.V1",
]


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = context.get("root") or context.get("os_root") or context.get("zroot") or "."
    reg_path = os.path.join(str(root), REG_REL)

    errors = []
    evidence: Dict[str, Any] = {"root": str(root), "registry": REG_REL}

    if not os.path.exists(reg_path):
        errors.append(f"MISSING:{REG_REL}")
        ok = False
        out = {"gate_id": GATE_ID, "p0": P0, "ok": ok, "errors": errors, "evidence": evidence}
        if ledger_writer is not None:
            ledger_writer({"event_type": "GATE_RESULT", **out})
        return out

    try:
        with open(reg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:  # noqa: BLE001
        errors.append(f"UNPARSEABLE:{REG_REL}:{type(e).__name__}:{e}")
        ok = False
        out = {"gate_id": GATE_ID, "p0": P0, "ok": ok, "errors": errors, "evidence": evidence}
        if ledger_writer is not None:
            ledger_writer({"event_type": "GATE_RESULT", **out})
        return out

    metagates = data.get("metagates", [])
    present = set(
        m.get("metagate_id")
        for m in metagates
        if isinstance(m, dict) and isinstance(m.get("metagate_id"), str)
    )
    missing = [m for m in REQUIRED if m not in present]

    if missing:
        errors.append(f"MISSING_REQUIRED_METAGATES:{missing}")

    # Byte-present check: ensure each registered path exists.
    missing_paths = []
    for m in metagates:
        if not isinstance(m, dict):
            continue
        mid = m.get("metagate_id")
        p = m.get("path")
        if mid in REQUIRED and isinstance(p, str):
            ap = os.path.join(str(root), p)
            if not os.path.exists(ap):
                missing_paths.append(p)
    if missing_paths:
        errors.append(f"MISSING_REQUIRED_METAGATE_PATHS:{missing_paths}")

    ok = len(errors) == 0
    evidence.update({"present": sorted(list(present))[:50], "required": REQUIRED})

    out = {"gate_id": GATE_ID, "p0": P0, "ok": ok, "errors": errors, "evidence": evidence}
    if ledger_writer is not None:
        ledger_writer({"event_type": "GATE_RESULT", **out})
    return out

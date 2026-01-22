# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: P0.BYTE_TRUTH (v2)

Purpose
- Enforce P0.INVARIANT.BYTE_TRUTH.V2 by blocking preflight when the OS
  is not byte-present or is a stub/scaffold.

Design
- Evidence-only: checks filesystem state; no inference.
- Deterministic: uses fixed required paths and minimum byte size threshold.

Inputs (context)
- root / os_root / zroot (string): OS root directory (defaults to '.')
- mb_min_os_bytes (int, optional): override stub threshold

Outputs
- gate result dict with ok/ errors suitable for ledger emission.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from metablooms.validators.mb_validate_byte_truth_v2 import validate_byte_truth_v2


GATE_ID = "GATE.P0.BYTE_TRUTH.V2"
P0 = True


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = context.get("root") or context.get("os_root") or context.get("zroot") or "."
    min_bytes = context.get("mb_min_os_bytes")
    if min_bytes is None:
        min_bytes = 1_000_000

    res = validate_byte_truth_v2(str(root), min_os_bytes=int(min_bytes))

    errors = [f"{f.kind}:{f.path}:{f.detail}" for f in res.findings]

    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": res.ok,
        "errors": errors,
        "evidence": {
            "root": str(root),
            "total_bytes": res.total_bytes,
            "min_os_bytes": int(min_bytes),
            "required_paths": ["BOOT_METABLOOMS.py", "metablooms", "SYSTEM_INDEX.json", "SHIP_MANIFEST.json"],
        },
    }

    if ledger_writer is not None:
        ledger_writer({
            "event_type": "GATE_RESULT",
            "gate_id": GATE_ID,
            "ok": res.ok,
            "errors": errors,
            "evidence": out["evidence"],
        })

    return out

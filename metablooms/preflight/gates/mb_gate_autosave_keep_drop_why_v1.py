# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: AUTOSAVE_KEEP_DROP_WHY (v1)

P0 preflight gate.

Purpose
- Validate presence + minimal integrity of KEEP/DROP/WHY governance artifacts.
- This gate is intentionally *wiring-only*: it does not attempt to enforce commit-time
  behavior inside preflight; commit-time enforcement is handled by autosave/export.

Contract
- Returns a structured dict compatible with the runtime preflight aggregator.
- Fails closed if required docs/ledgers are missing.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional


GATE_ID = "GATE.AUTOSAVE.KEEP_DROP_WHY.V1"
P0 = True


def _root_from_this_file() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _checks() -> List[str]:
    root = _root_from_this_file()
    schema = os.path.join(root, "governance", "KEEP_DROP_WHY_SCHEMA.md")
    ledger = os.path.join(root, "governance", "KEEP_DROP_WHY_LOG_APPEND_ONLY.md")

    errors: List[str] = []
    if not os.path.exists(schema):
        errors.append(f"missing schema doc: {schema}")
    if not os.path.exists(ledger):
        errors.append(f"missing append-only ledger: {ledger}")
    return errors


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    errors = _checks()
    ok = len(errors) == 0

    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": ok,
        "errors": errors,
        "mode_active": True,
        "bypass_used": False,
    }

    if ledger_writer is not None:
        ledger_writer({
            "event_type": "GATE_RESULT",
            "gate_id": GATE_ID,
            "ok": ok,
            "errors": errors,
        })

    return out


def main() -> int:
    """CLI-friendly entrypoint."""
    res = run_gate({})
    if not res["ok"]:
        for e in res["errors"]:
            print(f"GATE_FAIL:P0.AUTOSAVE.KEEP_DROP_WHY: {e}")
        return 2
    print("GATE_OK:P0.AUTOSAVE.KEEP_DROP_WHY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: DECISION.TRACE.WIRING (v1)

P0 preflight gate.

Purpose
- Fail-closed wiring check ensuring governed decision-trace artifacts exist.
- This gate does NOT attempt to expose private chain-of-thought.

Required files
- metablooms/governance/DECISION_TRACE_SCHEMA_v1.json
- metablooms/governance/DECISION_TRACE_APPEND_ONLY.jsonl
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional


GATE_ID = "GATE.DECISION.TRACE.WIRING.V1"
P0 = True


def _root_from_this_file() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _checks() -> List[str]:
    root = _root_from_this_file()
    schema = os.path.join(root, "governance", "DECISION_TRACE_SCHEMA_v1.json")
    ledger = os.path.join(root, "governance", "DECISION_TRACE_APPEND_ONLY.jsonl")

    errors: List[str] = []
    if not os.path.exists(schema):
        errors.append(f"missing decision trace schema: {schema}")
    if not os.path.exists(ledger):
        errors.append(f"missing decision trace ledger: {ledger}")

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
    res = run_gate({})
    if not res["ok"]:
        for e in res["errors"]:
            print(f"GATE_FAIL:P0.DECISION.TRACE.WIRING: {e}")
        return 2
    print("GATE_OK:P0.DECISION.TRACE.WIRING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

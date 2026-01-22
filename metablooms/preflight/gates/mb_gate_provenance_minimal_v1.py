# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: PROVENANCE.MIN3 (v1)

P0 preflight gate.

Purpose
- Fail-closed wiring check for the reduced provenance schema (MIN3).
- This gate validates presence of the schema doc that defines the required
  fields: origin, mutation_reason, supersedes.

Contract
- Returns a structured dict compatible with the runtime preflight aggregator.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional


GATE_ID = "GATE.PROVENANCE.MIN3.V1"
P0 = True


def _root_from_this_file() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _checks() -> List[str]:
    root = _root_from_this_file()
    schema = os.path.join(root, "governance", "PROVENANCE_SCHEMA_v1.md")
    errors: List[str] = []
    if not os.path.exists(schema):
        errors.append(f"missing provenance schema doc: {schema}")
        return errors

    # Minimal content check: ensure the 3 required field names appear.
    try:
        txt = open(schema, "r", encoding="utf-8").read()
    except Exception as e:  # noqa: BLE001
        errors.append(f"failed to read schema doc: {e}")
        return errors

    for token in ("origin", "mutation_reason", "supersedes"):
        if token not in txt:
            errors.append(f"schema doc missing required field token: {token}")

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
            print(f"GATE_FAIL:P0.PROVENANCE.MIN3: {e}")
        return 2
    print("GATE_OK:P0.PROVENANCE.MIN3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

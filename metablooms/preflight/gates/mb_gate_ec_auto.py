# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""Preflight gate: GATE.EC_AUTO.V1

Wiring-ready gate wrapper. Integrators should call `run_gate(context, ledger_writer)`
where:
- context is a dict built by the runtime
- ledger_writer is a callable that records pass/fail with error list

This file is intentionally small and strict.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from metablooms.validators.ec_auto_validate import validate_ec_auto


GATE_ID = "GATE.EC_AUTO.V1"
P0 = True


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    """Run the EC-AUTO gate.

    Returns a structured result dict suitable for preflight aggregation.
    """

    res = validate_ec_auto(context)

    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": res.ok,
        "mode_active": res.mode_active,
        "bypass_used": res.bypass_used,
        "errors": list(res.errors),
    }

    if ledger_writer is not None:
        ledger_writer({
            "event_type": "GATE_RESULT",
            "gate_id": GATE_ID,
            "ok": res.ok,
            "errors": list(res.errors),
            "mode_active": res.mode_active,
            "bypass_used": res.bypass_used,
        })

    return out

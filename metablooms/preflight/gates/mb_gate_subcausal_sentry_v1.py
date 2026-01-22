# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: SUBCAUSAL_SENTRY (v1)

P0 preflight gate.

Purpose
- Fail-closed wiring validation for the P0.SUBCAUSAL_SENTRY spec.
- This gate does NOT execute NLP detection; it only ensures the capability is
  present, minimally well-formed, and governed.

Contract
- Returns a structured dict compatible with the runtime preflight aggregator.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Dict, List, Optional

import yaml


GATE_ID = "GATE.SUBCAUSAL_SENTRY.V1"
P0 = True

REQUIRED_KEYS = [
    "id",
    "version",
    "priority",
    "mode",
    "purpose",
    "scope",
    "dc_mappings",
    "subcausal_signals",
    "escalation",
    "fail_closed",
]


def _spec_path() -> str:
    return os.path.join(os.path.dirname(__file__), "P0_SUBCAUSAL_SENTRY.yaml")


def _checks() -> List[str]:
    errors: List[str] = []
    path = _spec_path()
    if not os.path.exists(path):
        return [f"missing spec: {path}"]

    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
    except Exception as e:  # noqa: BLE001
        return [f"failed to parse yaml: {e}"]

    if not isinstance(spec, dict):
        return ["spec is not a mapping"]

    for k in REQUIRED_KEYS:
        if k not in spec:
            errors.append(f"spec missing required key: {k}")

    if spec.get("id") != "P0.SUBCAUSAL_SENTRY":
        errors.append("spec id mismatch (expected P0.SUBCAUSAL_SENTRY)")

    signals = spec.get("subcausal_signals")
    if not isinstance(signals, list) or len(signals) < 3:
        errors.append("expected subcausal_signals as list with >= 3 items")

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
            print(f"GATE_FAIL:P0.SUBCAUSAL_SENTRY: {e}")
        return 2
    print("GATE_OK:P0.SUBCAUSAL_SENTRY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

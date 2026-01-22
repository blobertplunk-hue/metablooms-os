# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: DECISION.TRACE.SCHEMA.VALIDATE (v1)

P0 preflight gate.

Validates that the decision trace ledger is readable JSONL and that each record
in a trailing window contains the required fields declared in the schema.

This gate does not attempt to expose private chain-of-thought.
"""

from __future__ import annotations

import json
from pathlib import Path

import os
from typing import Any, Callable, Dict, List, Optional

GATE_ID = "GATE.DECISION.TRACE.SCHEMA.VALIDATE.V1"
P0 = True

DEFAULT_TAIL_LINES = 50


def _root_from_this_file() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _read_schema_required_fields(schema_path: str) -> List[str]:
    obj = json.loads(Path(schema_path).read_text(encoding="utf-8"))
    req = obj.get("required_fields")
    if not isinstance(req, list) or not req:
        raise ValueError("schema missing required_fields list")
    return [str(x) for x in req]


def _tail_lines(path: str, n: int) -> List[str]:
    # Simple, portable tail for moderate file sizes.
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return lines[-n:] if n > 0 else lines


def _checks(tail_lines: int = DEFAULT_TAIL_LINES) -> List[str]:
    root = _root_from_this_file()
    schema = os.path.join(root, "governance", "DECISION_TRACE_SCHEMA_v1.json")
    ledger = os.path.join(root, "governance", "DECISION_TRACE_APPEND_ONLY.jsonl")

    errors: List[str] = []
    if not os.path.exists(schema):
        return [f"missing schema: {schema}"]
    if not os.path.exists(ledger):
        return [f"missing ledger: {ledger}"]

    try:
        required = _read_schema_required_fields(schema)
    except Exception as e:  # noqa: BLE001
        return [f"failed to read schema required_fields: {e}"]

    try:
        sample = _tail_lines(ledger, tail_lines)
    except Exception as e:  # noqa: BLE001
        return [f"failed to read ledger: {e}"]

    # Empty ledger is allowed at wiring time; orchestrator should populate on first run.
    if not sample:
        return []

    for i, raw in enumerate(sample, start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception as e:  # noqa: BLE001
            errors.append(f"invalid JSON at tail_line#{i}: {e}")
            continue

        if not isinstance(rec, dict):
            errors.append(f"non-object JSON at tail_line#{i}")
            continue

        rt = rec.get("record_type")
        if rt not in (None, "DECISION_TRACE"):
            errors.append(f"record_type mismatch at tail_line#{i}: {rt!r}")

        for k in required:
            if k not in rec:
                errors.append(f"missing field {k!r} at tail_line#{i}")

    return errors


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    tail_n = int(context.get("decision_trace_tail_lines", DEFAULT_TAIL_LINES) or DEFAULT_TAIL_LINES)
    errors = _checks(tail_n)
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
            print(f"GATE_FAIL:P0.DECISION.TRACE.SCHEMA.VALIDATE: {e}")
        return 2
    print("GATE_OK:P0.DECISION.TRACE.SCHEMA.VALIDATE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

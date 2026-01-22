# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: CODE.NO_PLACEHOLDERS (v1)

P0 preflight gate.

Purpose
- Fail-closed enforcement against omission placeholders and silent stubs in ship-path code.
- Primary target: accidental omissions that create rework and drift.

Notes
- This gate is deliberately narrow and auditable. It does not enforce style.
- It allows typing ellipsis (Callable[..., R]) and Tuple[T, ...].
- It allows exception marker classes (class MyError(Exception): pass).
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from metablooms.validators.mb_validate_no_placeholders_v1 import validate_no_placeholders


GATE_ID = "GATE.CODE.NO_PLACEHOLDERS.V1"
P0 = True


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = context.get("root") or context.get("os_root") or context.get("zroot") or "."
    res = validate_no_placeholders(str(root))

    errors = [f"{f.path}:{f.line}:{f.kind}:{f.detail}" for f in res.findings]

    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": res.ok,
        "errors": errors,
        "mode_active": True,
        "bypass_used": False,
    }

    if ledger_writer is not None:
        ledger_writer({
            "event_type": "GATE_RESULT",
            "gate_id": GATE_ID,
            "ok": res.ok,
            "errors": errors,
        })

    return out

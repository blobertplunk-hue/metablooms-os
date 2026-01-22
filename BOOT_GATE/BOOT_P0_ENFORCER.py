"""Boot-time P0 invariant enforcer.

Teeth:
- Executes every P0 invariant module from the registry.
- Writes an enforcement ledger row per invariant.
- Halts boot on first FAIL.

Non-prescriptive: this module enforces invariants; it does not propose remedies.
"""

from __future__ import annotations

import datetime
import importlib
import inspect
import json
import os
from typing import Any, Dict, Tuple

from .BOOT_P0_INVARIANT_REGISTRY import get_p0_invariants


ENFORCEMENT_LEDGER = "/mnt/data/metablooms_ledgers/p0_boot_enforcement.jsonl"


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _append(obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(ENFORCEMENT_LEDGER), exist_ok=True)
    with open(ENFORCEMENT_LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def _call_inv_run(mod, *, trigger: str, os_root_hint: str | None) -> Tuple[bool, Dict[str, Any]]:
    """Call an invariant module's run() in a signature-tolerant, fail-closed way."""
    fn = getattr(mod, 'run', None)
    if fn is None:
        return False, {"error": "INVARIANT_MISSING_RUN"}

    try:
        sig = inspect.signature(fn)
        params = sig.parameters
        kwargs: Dict[str, Any] = {"trigger": trigger}
        if os_root_hint is not None and "os_root_hint" in params:
            kwargs["os_root_hint"] = os_root_hint
        return fn(**kwargs)
    except TypeError:
        # If the invariant does not accept kwargs, attempt positional trigger only.
        return fn(trigger)


def enforce(trigger: str = "BOOT", os_root_hint: str | None = None) -> None:
    """Enforce all registered P0 boot invariants.

    Contract:
    - Accepts optional os_root_hint to align with BOOT_METABLOOMS.py.
    - Does not require invariants to accept os_root_hint; calls are signature-tolerant.
    """
    registry = get_p0_invariants()  # inv_id -> module path

    for inv_id in sorted(registry.keys()):
        mod_path = registry[inv_id]
        ts = _utc_now()
        try:
            mod = importlib.import_module(mod_path)
            ok, details = _call_inv_run(mod, trigger=trigger, os_root_hint=os_root_hint)
            _append({
                "inv_id": inv_id,
                "module": mod_path,
                "trigger": trigger,
                "os_root_hint": os_root_hint,
                "outcome": "PASS" if ok else "FAIL",
                "details": details,
                "timestamp": ts,
            })
            if not ok:
                raise SystemExit(f"BOOT_FAILED:P0_INVARIANT_FAIL:{inv_id}")
        except SystemExit:
            raise
        except Exception as e:  # noqa: BLE001
            _append({
                "inv_id": inv_id,
                "module": mod_path,
                "trigger": trigger,
                "os_root_hint": os_root_hint,
                "outcome": "ERROR",
                "details": {"error": str(e)},
                "timestamp": ts,
            })
            raise SystemExit(f"BOOT_FAILED:P0_INVARIANT_ERROR:{inv_id}")

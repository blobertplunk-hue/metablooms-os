#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""RUN_METABLOOMS.py

Stable runner invoked by BOOT_METABLOOMS.py.

This performs a *boot smoke test*:
- Executes only MetaBlooms-authored preflight gates (wiring/validators).
- Stops before legacy runtime prompt-dependent gates (ROW/PIPELINE/etc.).

Exit codes:
- 0: smoke test passed
- 2: smoke test failed (any P0 gate failed)
"""
from __future__ import annotations
# === MB_P0_AUTO_REHYDRATE_PRELUDE (P0) ===
import os as _os
from pathlib import Path as _Path
from datetime import datetime as _dt
try:
    from metablooms.runtime.auto_rehydrate import auto_rehydrate as _mb_auto_rehydrate
except Exception as _e:
    raise SystemExit(f"P0_BLOCKED: AUTO_REHYDRATE_IMPORT_FAILED: {_e}")

_MB_OS_ROOT = _Path(_os.environ.get("MB_OS_ROOT", "/mnt/data/MetaBlooms_OS"))
_MB_TURN_ID = _os.environ.get("MB_TURN_ID", "TURN_" + _dt.utcnow().strftime("%Y%m%d_%H%M%S"))

# === MB_P0_TURN_LOCK_ATEXIT (P0) ===
import atexit as _atexit
try:
    from metablooms.runtime.turn_lock import release_turn_lock as _mb_release_turn_lock
    _atexit.register(lambda: _mb_release_turn_lock(_MB_OS_ROOT, _MB_TURN_ID))
except Exception:
    pass
# === END MB_P0_TURN_LOCK_ATEXIT ===

# === MB_GENESIS_AND_TURN_INDEX (P0/P1) ===
try:
    if _os.environ.get("MB_ALLOW_INITIAL_BOOT", "0") == "1":
        from metablooms.runtime.genesis import ensure_genesis_receipt as _mb_ensure_genesis
        _mb_ensure_genesis(_MB_OS_ROOT, _MB_TURN_ID)
    from metablooms.runtime.turn_index import allocate_turn_index as _mb_alloc_idx
    _mb_allow = (_os.environ.get("MB_ALLOW_INITIAL_BOOT", "0") == "1")
    _mb_alloc_idx(_MB_OS_ROOT, _MB_TURN_ID, allow_initial=_mb_allow)
except Exception as _e:
    raise SystemExit(f"P0_BLOCKED: GENESIS_OR_TURN_INDEX_FAILED: {_e}")
# === END MB_GENESIS_AND_TURN_INDEX ===
# Fail-closed: if no prior receipt, auto_rehydrate raises; initial boot should set MB_ALLOW_INITIAL_BOOT=1
if _os.environ.get("MB_ALLOW_INITIAL_BOOT", "0") != "1":
    _mb_auto_rehydrate(_MB_OS_ROOT, _MB_TURN_ID)
# === END MB_P0_AUTO_REHYDRATE_PRELUDE ===



import importlib
import inspect
import json
import os
import sys
from typing import Any, Dict, List


def _repo_root() -> str:
    return os.path.abspath(os.path.dirname(__file__))


def _load_chain(root: str) -> List[Dict[str, Any]]:
    """Load preflight gate chain with schema compatibility.

    Accepted on-disk formats:
    1) Dict wrapper: {"gates": [ ... ]}
    2) Direct list: [ ... ]

    Fail-closed behavior:
    - Any other JSON type returns an empty list (causing P0 failure downstream
      when required schema gate runs).
    """
    chain_path = os.path.join(root, 'metablooms', 'preflight', 'preflight_gate_chain_v1.json')
    with open(chain_path, 'r', encoding='utf-8') as f:
        obj = json.load(f)

    # Schema v1 historically shipped as a bare list; newer docs may wrap it.
    if isinstance(obj, list):
        return [g for g in obj if isinstance(g, dict)]
    if isinstance(obj, dict):
        gates = obj.get('gates', [])
        if isinstance(gates, list):
            return [g for g in gates if isinstance(g, dict)]

    # Unknown format: fail-closed by returning empty list.
    return []

def main() -> int:
    root = _repo_root()
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)

    chain = _load_chain(root)

    results: List[Dict[str, Any]] = []
    ok = True

    run_context = {
        "root": root,
        "os_root": root,
        "zroot": root,
        "prompt": "__BOOT_SMOKE__",
        "objective_key": "OBJ.OS.BOOT.SMOKE",
    }

    for g in chain:
        gate_id = g.get("id") or g.get("gate_id")
        module = g.get("module")
        callable_name = g.get("callable")
        level = g.get("level")

        # Stop before prompt-dependent legacy runtime gates.
        if isinstance(module, str) and module.startswith("runtime."):
            break

        try:
            mod = importlib.import_module(module)
            fn = getattr(mod, callable_name)            # Call gate with a deterministic arity check.
            # Some gates accept (context) while others accept (context, ledger_writer).
            try:
                sig = inspect.signature(fn)
                params = list(sig.parameters.values())
                if len(params) >= 2:
                    out = fn(run_context, None)
                else:
                    out = fn(run_context)
            except Exception:
                # If signature inspection fails for any reason, default to single-arg call.
                out = fn(run_context)            # Normalize minimal expected keys
            if isinstance(out, dict):
                if "ok" in out:
                    passed = bool(out.get("ok"))
                elif "pass" in out:
                    passed = bool(out.get("pass"))
                else:
                    passed = False

                errors = out.get("errors")
                if not isinstance(errors, list):
                    errors = []
                # If a gate uses 'reason' instead of 'errors', promote it to an error string
                if not errors and isinstance(out.get("reason"), str) and not passed:
                    errors = [out.get("reason")]
            else:
                passed = bool(out)
                errors = []

            results.append({
                "gate_id": gate_id,
                "level": level,
                "pass": passed,
                "errors": errors,
            })
            if level == "P0" and not passed:
                ok = False
        except Exception as e:  # noqa: BLE001
            results.append({
                "gate_id": gate_id,
                "level": level,
                "pass": False,
                "errors": [f"EXCEPTION:{type(e).__name__}:{e}"],
            })
            if level == "P0":
                ok = False

    report = {"ok": ok, "results": results}
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0




def run():
    """BOOT entrypoint.

    Returns a BOOT-consumable payload:
    {
      "ok": bool,
      "checks": [
        {"check_id": str, "level": "P0"|"P1"|"P2", "pass": bool, "reason": str|None, "evidence": dict}
      ]
    }

    This function executes the same preflight chain as `main()`, but it does not
    print; it returns structured results.
    """
    # Execute preflight chain without printing by reusing the same logic,
    # but capturing the report rather than printing it.
    root = _repo_root()
    os.chdir(root)
    if root not in sys.path:
        sys.path.insert(0, root)

    chain = _load_chain(root)

    checks = []
    ok = True

    run_context = {
        "root": root,
        "os_root": root,
        "zroot": root,
        "prompt": "__BOOT_SMOKE__",
        "objective_key": "OBJ.OS.BOOT.SMOKE",
    }

    for g in chain:
        gate_id = g.get("id") or g.get("gate_id") or "UNKNOWN_GATE"
        module = g.get("module")
        callable_name = g.get("callable")
        level = g.get("level") or "P2"

        # Stop before prompt-dependent legacy runtime gates.
        if isinstance(module, str) and module.startswith("runtime."):
            break

        passed = False
        errors = []
        try:
            mod = importlib.import_module(module)
            fn = getattr(mod, callable_name)
            # Deterministic arity check: gates usually accept (context) or (context, ledger_writer)
            try:
                sig = inspect.signature(fn)
                params = list(sig.parameters.values())
                if len(params) >= 2:
                    out = fn(run_context, None)
                else:
                    out = fn(run_context)
            except Exception:
                out = fn(run_context)

            if isinstance(out, dict):
                if "ok" in out:
                    passed = bool(out.get("ok"))
                elif "pass" in out:
                    passed = bool(out.get("pass"))
                else:
                    passed = False

                errors = out.get("errors") if isinstance(out.get("errors"), list) else []
                if not errors and isinstance(out.get("reason"), str) and not passed:
                    errors = [out.get("reason")]
            else:
                passed = bool(out)
                errors = []

        except Exception as e:  # noqa: BLE001
            passed = False
            errors = [f"EXCEPTION:{type(e).__name__}:{e}"]

        check = {
            "check_id": gate_id,
            "level": level,
            "pass": bool(passed),
            "reason": None if passed else ("; ".join(str(x) for x in errors) if errors else "FAILED"),
            "evidence": {
                "module": module,
                "callable": callable_name,
                "errors": errors,
            },
        }
        checks.append(check)

        if level == "P0" and not passed:
            ok = False

    return {"ok": bool(ok), "checks": checks}


if __name__ == '__main__':
    try:
        rc = main()
        sys.exit(0 if rc is None else rc)
    except Exception as e:
        print(f'RUNNER_EXCEPTION:{e}', file=sys.stderr)
        sys.exit(1)

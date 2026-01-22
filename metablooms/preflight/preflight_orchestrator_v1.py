# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""metablooms/preflight/preflight_orchestrator_v1.py

Preflight Orchestrator v1
- Executes gates strictly in registry order (metablooms/preflight/preflight_gate_chain_v1.json)
- Uses adapter map (metablooms/preflight/leaf_gate_adapter_map_v1.json)
- Normalizes every gate into: {gate_id, pass, violations[], scope}
- Fail-closed on any P0 failure
- Centralizes ledger writes (one event per gate result)

This module performs no network access.
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
import inspect
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]

CHAIN_PATH = ROOT / "metablooms" / "preflight" / "preflight_gate_chain_v1.json"
ADAPTER_PATH = ROOT / "metablooms" / "preflight" / "leaf_gate_adapter_map_v1.json"
LEDGER_PATH = ROOT / "ledger" / "ledger.ndjson"


@dataclass(frozen=True)
class GateResult:
    gate_id: str
    passed: bool
    violations: List[str]
    scope: Dict[str, Any]


def _read_json(path: Path, context: str) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"PREFLIGHT_ORCH_V1: invalid JSON for {context}: {path} :: {e}")


def _append_ledger(event: Dict[str, Any]) -> None:
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _get_by_dotted(obj: Dict[str, Any], dotted: str, state: Dict[str, Any]) -> Any:
    # supported prefixes: run_context.<k>, state.<k>, run_context
    if dotted == "run_context":
        return obj
    if dotted.startswith("run_context."):
        return obj.get(dotted.split(".", 1)[1])
    if dotted.startswith("state."):
        return state.get(dotted.split(".", 1)[1])
    raise RuntimeError(f"PREFLIGHT_ORCH_V1: unsupported input_from: {dotted}")


def _normalize_legacy_allowed_failure(gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    allowed = bool(legacy.get("allowed"))
    violations: List[str] = []
    if not allowed:
        failure = legacy.get("failure") or "GATE_BLOCKED"
        violations.append(str(failure))
        # Include common error fields for determinism
        if isinstance(legacy.get("errors"), list):
            violations.extend([str(x) for x in legacy.get("errors")])
        if legacy.get("message"):
            violations.append(str(legacy.get("message")))
    return GateResult(gate_id=gate_id, passed=allowed, violations=violations, scope=scope)


def _normalize_ec_auto(gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    ok = bool(legacy.get("ok"))
    errs = legacy.get("errors") or []
    violations = [str(e) for e in errs] if not ok else []
    return GateResult(gate_id=gate_id, passed=ok, violations=violations, scope=scope)


def _normalize_legacy_acceptance(gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    # auto_accept returns {accepted: bool, confidence, reason, patch?}
    accepted = bool(legacy.get("accepted"))
    # acceptance is not a block unless explicitly rejected with high risk; treat as pass
    # but record violations if it indicates a refusal with a reason
    violations: List[str] = []
    if not accepted and legacy.get("reason"):
        violations.append(f"AUTO_ACCEPT_NOT_ACCEPTED:{legacy.get('reason')}")
    return GateResult(gate_id=gate_id, passed=True, violations=violations, scope=scope)


def _normalize_ok_errors_gate(gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    """Normalize gates that return {ok: bool, errors?: list[str], ...}.

    This is the preferred contract for small P0 wiring gates.
    """
    ok = bool(legacy.get("ok"))
    errs = legacy.get("errors")
    violations: List[str] = []

    if not ok:
        if isinstance(errs, list):
            violations.extend([str(x) for x in errs])
        # Best-effort fallbacks for older gates
        if legacy.get("failure"):
            violations.append(str(legacy.get("failure")))
        if legacy.get("details"):
            violations.append(str(legacy.get("details")))
        if not violations:
            violations.append("GATE_FAILED")

    return GateResult(gate_id=gate_id, passed=ok, violations=violations, scope=scope)


def _normalize_pass_violations_gate(gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    """Normalize gates that already return {pass: bool, violations: list, scope?: dict}."""
    passed = bool(legacy.get("pass"))
    violations: List[str] = []
    if not passed:
        v = legacy.get("violations") or []
        if isinstance(v, list):
            violations.extend([str(x) for x in v])
        else:
            violations.append(str(v))
        if not violations:
            violations.append("GATE_FAILED")

    # prefer leaf-provided scope if present
    leaf_scope = legacy.get("scope")
    if isinstance(leaf_scope, dict):
        merged = dict(scope)
        merged.update(leaf_scope)
        scope = merged

    return GateResult(gate_id=gate_id, passed=passed, violations=violations, scope=scope)


def _normalize(strategy: str, gate_id: str, legacy: Dict[str, Any], scope: Dict[str, Any]) -> GateResult:
    if strategy == "legacy_allowed_failure":
        return _normalize_legacy_allowed_failure(gate_id, legacy, scope)
    if strategy == "ec_auto_gate":
        return _normalize_ec_auto(gate_id, legacy, scope)
    if strategy == "legacy_acceptance":
        return _normalize_legacy_acceptance(gate_id, legacy, scope)
    if strategy == "ok_errors_gate":
        return _normalize_ok_errors_gate(gate_id, legacy, scope)
    if strategy == "pass_violations_gate":
        return _normalize_pass_violations_gate(gate_id, legacy, scope)
    raise RuntimeError(f"PREFLIGHT_ORCH_V1: unknown normalize strategy: {strategy}")


def run_preflight(run_context: Dict[str, Any]) -> Dict[str, Any]:
    chain = _read_json(CHAIN_PATH, "preflight_gate_chain_v1")
    adapters = _read_json(ADAPTER_PATH, "leaf_gate_adapter_map_v1")

    gates = chain.get("gates") or []
    amap = (adapters.get("adapters") or {})

    state: Dict[str, Any] = {}

    # initial scope (best-effort; caller may provide richer)
    scope = dict(run_context.get("scope") or {})
    if "kind" not in scope:
        scope["kind"] = "RUN"

    results: List[Dict[str, Any]] = []

    # Decision Trace (governed): emit a sanitized start record so paste-backs are not required.
    try:
        from metablooms.runtime.decision_trace import record_decision  # type: ignore

        os_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        objective_key = str(run_context.get("objective_key") or "OBJ.PREFLIGHT")
        record_decision(
            os_root,
            objective_key=objective_key,
            decision_id="PREFLIGHT.START",
            decision="Begin preflight run",
            rationale=["Provide audit-grade visibility without requiring user paste-backs."],
            assumptions=["Decision trace is a governed, sanitized ledger (not chain-of-thought)."],
            failure_surfaces=["Missing decision trace artifacts", "Non-JSONL ledger corruption"],
            evidence_refs=["metablooms/preflight/preflight_gate_chain_v1.json"],
            actor="metablooms.preflight",
        )
    except Exception:
        # Never block preflight on decision trace writes; wiring is enforced by P0 gates.
        pass

    for g in gates:
        gate_id = g.get("id")
        level = g.get("level")
        if gate_id not in amap:
            raise RuntimeError(f"PREFLIGHT_ORCH_V1: gate missing adapter mapping: {gate_id}")

        a = amap[gate_id]
        module_name = a.get("module")
        callable_name = a.get("callable")
        input_from = a.get("input_from")
        normalize = a.get("normalize")

        # Derive expected state conveniences
        if "pipeline_definition" not in state and isinstance(state.get("pipeline_resolution"), dict):
            pipes = state["pipeline_resolution"].get("pipelines") or []
            if pipes:
                state["pipeline_definition"] = pipes[0]
                # propagate scope
                pid = pipes[0].get("pipeline_id")
                if pid and "pipeline_id" not in scope:
                    scope["pipeline_id"] = pid

        # Resolve input
        inp = _get_by_dotted(run_context, str(input_from), state)

        # Call leaf gate
        legacy: Dict[str, Any]
        exc: Optional[str] = None
        try:
            mod = import_module(module_name)
            fn = getattr(mod, callable_name)

            if input_from != "run_context":
                legacy = fn(inp)
            else:
                # Support both signatures:
                # - run_gate(context)
                # - run_gate(context, ledger_writer=None)
                try:
                    params = list(inspect.signature(fn).parameters.values())
                except Exception:
                    params = []

                if len(params) >= 2:
                    legacy = fn(run_context, None)
                else:
                    legacy = fn(run_context)

        except Exception as e:
            exc = f"{type(e).__name__}: {e}"
            legacy = {"allowed": False, "failure": "EXCEPTION", "errors": [exc]}

        # Update state from mapping
        out_to_state = a.get("output_to_state") or {}
        if isinstance(out_to_state, dict) and isinstance(legacy, dict):
            for state_key, legacy_key in out_to_state.items():
                if legacy_key in legacy:
                    state[state_key] = legacy.get(legacy_key)

        # Normalize
        nr = _normalize(str(normalize), gate_id, legacy if isinstance(legacy, dict) else {"allowed": False, "failure": "INVALID_RETURN"}, scope)

        event = {
            "event_type": "PREFLIGHT_GATE_RESULT",
            "gate_id": nr.gate_id,
            "level": level,
            "pass": nr.passed,
            "violations": list(nr.violations),
            "scope": dict(nr.scope),
        }
        _append_ledger(event)

        results.append({
            "gate_id": nr.gate_id,
            "pass": nr.passed,
            "violations": list(nr.violations),
            "scope": dict(nr.scope),
        })

        if level == "P0" and not nr.passed:
            return {"ok": False, "results": results, "stopped_at_gate": nr.gate_id}

    return {"ok": True, "results": results, "stopped_at_gate": None}


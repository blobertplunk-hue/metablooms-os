# Leaf Gate Contract v1

## Purpose
A Leaf Gate is a **pure validator** invoked by the Preflight Orchestrator. Leaf gates must not mutate state.

## Callable
A leaf gate MUST expose a single callable specified by the adapter map:

- `callable(context) -> legacy_result`

The orchestrator supplies `context` as dictated by `leaf_gate_adapter_map_v1.json`.

## Purity requirements (non-negotiable)
Leaf gates MUST NOT:
- write any ledger files
- modify any registries / indexes
- perform network access
- write output artifacts
- call promotion / patch acceptance routines with side effects

## Failure semantics
Leaf gates MAY raise exceptions, but the orchestrator will treat exceptions as **failures** and will capture:
- exception type
- message

Leaf gates MAY return legacy-shaped dicts (e.g., `{allowed: bool, failure: str, ...}`), but they will be normalized by the orchestrator into the canonical leaf-gate result.

## Canonical normalized result (owned by orchestrator)
The orchestrator MUST normalize each leaf gate into:

```json
{
  "gate_id": "GATE.<...>",
  "pass": true,
  "violations": ["..."],
  "scope": {"kind": "RUN", "row": null, "pipeline_id": null}
}
```


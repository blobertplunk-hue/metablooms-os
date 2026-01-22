# Preflight Orchestrator Contract v1

## Authority
The Preflight Orchestrator is the **single authoritative executor** of preflight validation.

It owns:
- gate execution order (via `preflight_gate_chain_v1.json`)
- fail-closed semantics (P0 stops the run)
- normalization into canonical results
- centralized ledger writes for gate results

## Inputs
- `run_context` (dict): minimum required keys:
  - `prompt` (str)
  - optional: `row_resolution`, `pipeline_resolution`, `pipeline_definition`, `scope`

## Gate execution
- Load ordered gate list from `metablooms/preflight/preflight_gate_chain_v1.json`.
- For each gate, load invocation/normalization from `metablooms/preflight/leaf_gate_adapter_map_v1.json`.
- Execute strictly in order.
- If a gate is marked `P0` and fails, stop immediately and return failure.

## Output
Returns a structured summary:

```json
{
  "ok": true,
  "results": [ {"gate_id":"...","pass":true,"violations":[],"scope":{}} ],
  "stopped_at_gate": null
}
```

## Ledger
- The orchestrator MUST write one ledger event per gate result.
- Leaf gates MUST NOT write ledger.

## Network boundary
- No network access during preflight.

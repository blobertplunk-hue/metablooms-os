# RIDIE Persistence: Does it make improvements persist?
Date: 2026-01-08

## What your current RIDIE delta does (v1.0)
Your uploaded delta `2026-01-08_metablooms_delta_RIDIE_v1_0.json` registers a `RIDIEEngine` module and a smoke test, and appends it to `MODULE_REGISTRY.json`.
It **does not** include any mechanism to persist “mutations” or process improvements across runs by itself.

## What “persistence” must mean in MetaBlooms
For improvements to persist safely, you need *two* things:
1. **Durable storage** of proposed changes (append-only log + checkpoint state)
2. **Promotion gate** so proposals are applied only when explicitly approved/validated

## What this new delta adds (v1.1)
- `modules/ridie_persistence.py`
  - appends proposals to `ridie/proposals.ndjson` (append-only)
  - writes `ridie/state.json` as a checkpoint (last stage + thresholds)
- a hook patch placeholder for `kernel/stage_runner.py` so stage results can carry:
  - `ridie_mutations` (list of proposals)
  - `ridie_state` (checkpoint dict)
- a deterministic smoke test

## What it still does NOT do (by design)
- It does not auto-apply proposals to canonical artifacts.
- It does not collapse standards.
- It does not rewrite prior stage outputs.

## Outcome
After this delta is integrated, RIDIE can improve MetaBlooms processes *persistently* by:
- saving what it learned (thresholds, stop policy tuning, recommendations)
- enabling later gated promotion into kernel rules/process configs

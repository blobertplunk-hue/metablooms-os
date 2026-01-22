# Experiential Learning Engine (ELE) — v1

## Scope
ELE is a governed, append-only capture of experiential learning cycles:
- prompt → observations → hypotheses → actions → results
- status tracking (open/closed/superseded)

ELE is a learning subsystem. Hanging Threads may reference ELE cycles, but ELE does not depend on Hanging Threads.

## Storage
- `data/experiential_learning/cycles.ndjson` (append-only; last-write-wins per cycle_id)

## Boot behavior
- Non-fatal surfacing of open cycles via `engines/experiential_learning/boot_hook.py`.

## Governance
- Schema: `schemas/experiential_learning_cycle.schema.json`

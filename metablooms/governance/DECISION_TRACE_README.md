# Decision Trace (Governed) — v1

Purpose: provide an auditable, append-only record of **decisions** made during MetaBlooms workflows (wiring, audits, exports, refactors), without exposing private chain-of-thought.

## What this is
A **sanitized** decision log intended to answer:
- What decision was made?
- Why was it made?
- What assumptions were present?
- What failure surfaces were considered?
- What evidence artifacts support the decision?

## What this is not
- Raw model chain-of-thought
- Hidden deliberation tokens
- A guarantee that every micro-step is recorded

## Record location
- Schema: `metablooms/governance/DECISION_TRACE_SCHEMA_v1.json`
- Ledger (append-only): `metablooms/governance/DECISION_TRACE_APPEND_ONLY.jsonl`

## Minimum record (recommended)
Each line of the JSONL ledger should be a JSON object containing the required fields from the schema.

## Suggested "objective_key" convention
- `OBJ.OS.WIRE.P0`
- `OBJ.OS.EXPORT.CANONICAL`
- `OBJ.OS.AUDIT.PREFLIGHT`
- `OBJ.RUNTIME.LEARNING_TRIGGER`

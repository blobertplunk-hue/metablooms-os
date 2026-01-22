# THREAD_TIERING_GATE_SPEC_v1

## Purpose
This spec defines the **Tiering + Promotion Gate** for MetaBlooms CTOS Hanging Threads.

A *Hanging Thread* is a **stateful object** (a transactional unit of work), not a casual note.

## Thread record (NDJSON) minimum schema
Each line is a JSON object with:

Required:
- `thread_id` (string; stable identifier)
- `transaction_id` (string; unique transaction identifier)
- `tier` (integer; 1..3)
- `status` (string; controlled vocabulary)
- `summary` (string)
- `created_utc` (string; ISO-8601 UTC)

Optional:
- `roi_score` (number)
- `confidence` (number)
- `tags` (array[string])
- `source_refs` (array)
- `contradicts` (array)
- `last_updated_utc` (string)
- `compensation` (object) — compensating action record (Saga pattern)

## Status vocabulary
Open:
- `open`
- `blocked`
- `in_progress`

Closed:
- `resolved`
- `tied_off`
- `closed`
- `done`
- `archived`

## Tier semantics (HITL)
Tier-1: Schema/format fixes — full auto.
Tier-2: Logic/ROI — propose clusters; human selects priority.
Tier-3: Shipping/governance contradictions — **hard block**.

## Hard-block rule
If any record has:
- `tier == 3` AND `status ∈ {open, blocked, in_progress}`

then the system must fail closed with:
- `TIER3_THREADS_PRESENT`

## Implementation
Validator:
- `validators/validate_thread_tiering_gate_v1.py`
Registry:
- `VALIDATOR_REGISTRY.json` entry: `THREAD_TIERING_GATE_V1`
Stage:
- `boot` (preflight gate chain)


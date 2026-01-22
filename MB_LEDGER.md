# MB_LEDGER

MetaBlooms uses an **append-only, hash-chained NDJSON ledger** to record boot, validation, module activation, and shipping decisions.

## Why this exists
- Creates a **mechanically enforced bridge** between “what we decided / claimed” and what was actually done on disk.
- Enables reliable RCA by providing an immutable, time-ordered evidence trail.

## Files
- `ledger/ledger.ndjson` — append-only event log (one JSON object per line)
- `ledger/ledger_event.schema.json` — minimal event schema
- `ledger/metablooms_ledger.py` — writer + verifier (no third-party deps)

## Hash chaining
Each event includes:
- `prev_hash` — SHA256 of the previous event line’s `hash` (or `GENESIS`)
- `hash` — SHA256 of the canonical JSON of the event with `hash` blanked

This makes tampering detectable.

## Boot integration
`BOOT_METABLOOMS.py`:
- initializes a ledger writer at boot start
- records validations and failures
- records `BOOT_OK` / `BOOT_HALT`
- verifies ledger chain at end (`LEDGER_VERIFY`)

## Minimal expectation (fail-closed philosophy)
If governance requires proof of actions, those actions must be reflected in the ledger (or the system should refuse to claim them).

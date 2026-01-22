# KEEP / DROP / WHY — Required Ledger Schema (v1)

## Purpose
Convert design decisions into durable training signals and prevent silent drift.

## When Required
A KEEP/DROP/WHY record MUST be written for:
- any `WIRE THIS IN NOW` commit
- any rename/deprecation
- any new P0/P1 gate or invariant

## Schema (required fields)
- `timestamp`
- `objective_key`
- `change_type` (ADD | UPDATE | DEPRECATE | DROP | RENAME)
- `keep` (list of kept elements)
- `drop` (list of dropped elements)
- `why_keep` (short rationale)
- `why_drop` (short rationale)
- `supersedes` (what this replaces, if anything)

## Fail-Closed Rule
If a commit occurs without a KEEP/DROP/WHY record, the autosave export is invalid.

# Delta Intake & Forward-Port — Module Manifest v1

Purpose: Safely ingest "delta" artifacts created against older OS versions and forward-port their intent into the current OS line.

Core idea:
- Treat deltas as **intent specifications**, not byte-perfect patches.
- Create a deterministic translation path: INTENT → TARGET SEGMENTS → OVERLAY → RECEIPTS.

Modes:
- DISABLED
- P0_WARN (log issues, continue)
- P0_STRICT (fail-closed on missing intent fields / unsafe ops)

Outputs (receipts):
- DELTA_INTAKE_RECEIPT.json
- FORWARDPORT_PLAN.md
- FORWARDPORT_DIFF.md
- MERGE_DECISION.json

Fail-closed rules:
- No file deletion by default.
- No overwrite of immutable entrypoints.
- Any conflicting artifact triggers PROMOTION_BLOCKED unless explicitly resolved.

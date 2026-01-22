# WORKFLOW_PREFLIGHT_AUDIT_SOP_v1 (Fail-Closed)

## Purpose
Prevent "audit drift" and silent non-execution by making preflight audits deterministic,
schema-valid, and publishable only when internally consistent.

## Inputs
- Target ZIP bundle (canonical or candidate)
- Extract destination (fresh directory)

## Required Steps (in order)
1. Extract target ZIP to a **fresh** audit directory.
2. Locate `metablooms/preflight/preflight_gate_chain_v1.json`.
3. Validate chain schema (FAIL if mixed `id` / `gate_id`).
4. Discover available gate modules under `metablooms/preflight/gates/mb_gate_*_v1.py`.
5. Load the Expected Gate Set for this release/tag (explicit list, not inferred).
6. Compute diff:
   - expected_not_registered
   - registered_missing_modules
   - schema_violations
   - p0_ordering_violations
7. Generate audit JSON using the locked report schema.
8. Validate audit JSON via `metablooms/validators/mb_validate_preflight_audit_report_v1.py` (FAIL if errors).
9. Render audit Markdown **from the JSON** (no independent authoring).
10. Package the audit bundle ZIP with JSON+MD; verify the ZIP contains exactly those two files.

## Publication Rule
If any FAIL exists, the release cannot be tagged canonical.

## Canonical Gate Requirements
- `GATE.CHAIN.SCHEMA.V1` MUST be registered as P0 and MUST execute before any P1+ gate.

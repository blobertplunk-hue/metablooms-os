# MetaBlooms Append-Only Changelog

## 2026-01-16T00:10-0600 — AUTOSAVE EXPORT #002
- origin: "User directive to translate early runtime and formalize sub-causal sentry + governance schemas"
- mutation_reason: "Promote leading-indicator learning triggers and convert KEEP/DROP/WHY + provenance into enforced OS primitives"
- supersedes: "2026-01-16_metablooms_autosave_export_001.zip"

### Added
- P0.SUBCAUSAL_SENTRY specification + wiring gate
- KEEP/DROP/WHY schema + append-only ledger + autosave gate
- Reduced provenance schema (3 fields) + wiring gate
- Early runtime → current OS translation map

## 2026-01-16T00:45-0600 — AUTOSAVE EXPORT #003
- origin: "User directive to wire in chain schema gate + audit report schema validation"
- mutation_reason: "Prevent silent non-execution and audit-report drift by enforcing gate-chain key consistency and locked report schema"
- supersedes: "2026-01-16_metablooms_autosave_export_002.zip"

### Added
- P0 gate: GATE.CHAIN.SCHEMA.V1 (fails closed on mixed id/gate_id schemas)
- Validator: mb_validate_preflight_audit_report_v1.py (locked JSON schema)
- SOP: WORKFLOW_PREFLIGHT_AUDIT_SOP_v1 (fail-closed audit procedure)
- Updated: preflight_gate_chain_v1.json normalized to 'id' key for ECL gate entry


## 2026-01-16T01:10-0600 — AUTOSAVE EXPORT #004
- origin: "User directive to wire missing P0 gates and export canonical v1.1.2"
- mutation_reason: "Ensure new governed capabilities (SUBCAUSAL_SENTRY, KEEP/DROP/WHY, PROVENANCE.MIN3) are actually enforced by preflight by registering them as P0 gates and normalizing their callable contracts."
- supersedes: "2026-01-16_metablooms_autosave_export_003.zip"

### Added / Wired
- Registered P0 gates in `metablooms/preflight/preflight_gate_chain_v1.json`:
  - GATE.AUTOSAVE.KEEP_DROP_WHY.V1
  - GATE.SUBCAUSAL_SENTRY.V1
  - GATE.PROVENANCE.MIN3.V1

### Updated
- Normalized gate callable contract for the three gates above to `run_gate(context, ledger_writer=None) -> dict`.

## 2026-01-16T01:55-0600 — AUTOSAVE EXPORT #005
- origin: "User request to improve OS code + ensure P0 gate wiring is truly enforced"
- mutation_reason: "Close the remaining preflight wiring gap: chain-registered gates must also have leaf adapters + orchestrator must support both 1-arg and 2-arg leaf signatures without crashing."
- supersedes: "2026-01-16_metablooms_autosave_export_004.zip"

### Added / Wired
- Completed `leaf_gate_adapter_map_v1.json` coverage for all chain gates:
  - GATE.CHAIN.SCHEMA.V1
  - GATE.AUTOSAVE.KEEP_DROP_WHY.V1
  - GATE.SUBCAUSAL_SENTRY.V1
  - GATE.PROVENANCE.MIN3.V1
  - GATE.EXCODE.ECL.V1

### Updated
- `preflight_orchestrator_v1` now supports both leaf call signatures:
  - `fn(context)`
  - `fn(context, ledger_writer=None)`
- Added normalize strategies:
  - `ok_errors_gate`
  - `pass_violations_gate`

## 2026-01-16T01:40-0600 — AUTOSAVE EXPORT #006
- origin: "User directive to expose decisions (not chain-of-thought) via Extraordinary Coding + governed decision trace"
- mutation_reason: "Provide audit-grade visibility into decision points while respecting non-exposure of private chain-of-thought; enforce wiring via P0 gate."
- supersedes: "2026-01-16_metablooms_autosave_export_005.zip"

### Added / Wired
- Governance: Decision Trace schema + append-only ledger (JSONL)
  - metablooms/governance/DECISION_TRACE_SCHEMA_v1.json
  - metablooms/governance/DECISION_TRACE_APPEND_ONLY.jsonl
  - metablooms/governance/DECISION_TRACE_README.md
- Runtime helper: metablooms/runtime/decision_trace.py
- P0 gate: GATE.DECISION.TRACE.WIRING.V1
- Preflight wiring updates:
  - preflight_gate_chain_v1.json registered new P0 gate
  - leaf_gate_adapter_map_v1.json adapter registered

## 2026-01-16T02:25-0600 — AUTOSAVE EXPORT #007
- origin: "User directive to make Activity-phase improvements real: auto-capture governed decisions so paste-backs are optional"
- mutation_reason: "Wire a Decision Trace schema validator gate and auto-emit a sanitized preflight-start record to reduce reliance on manual paste-back evidence while preserving fail-closed governance."
- supersedes: "2026-01-16_metablooms_autosave_export_006.zip"

### Added / Wired
- P0 gate: GATE.DECISION.TRACE.SCHEMA.VALIDATE.V1
- Decision trace schema validation gate registered in:
  - metablooms/preflight/preflight_gate_chain_v1.json
  - metablooms/preflight/leaf_gate_adapter_map_v1.json

### Updated
- preflight_orchestrator_v1 now emits a sanitized Decision Trace record at preflight start (non-blocking).

## 2026-01-16T02:25-0600 — AUTOSAVE EXPORT #009
- origin: "User directive to wire in NO_SWALLOWED_EXCEPTIONS + enforce NO_PLACEHOLDERS (ellipsis/TODO/stubs)"
- mutation_reason: "Reduce rework and boot drift by blocking omission placeholders and silent exception swallowing; normalize gate-chain ordering (P0 before P1) and ensure adapter coverage."
- supersedes: "2026-01-16_metablooms_autosave_export_008.zip"

### Added / Wired
- P0 gate: `GATE.CODE.NO_PLACEHOLDERS.V1`
  - Gate: `metablooms/preflight/gates/mb_gate_no_placeholders_v1.py`
  - Validator: `metablooms/validators/mb_validate_no_placeholders_v1.py`
- P1 gate: `GATE.CODE.NO_SWALLOWED_EXCEPTIONS.V1` (WARN)
  - Gate + validator from delta `2026-01-16_delta_no_swallowed_exceptions_p1warn_v1.zip`
- Preflight wiring updates:
  - `preflight_gate_chain_v1.json` normalized and ordered
  - `leaf_gate_adapter_map_v1.json` adapter coverage ensured

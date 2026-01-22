# MetaBlooms Invariants Manifest (Human-Readable)

Generated UTC: 2026-01-10
Bundle lineage: MetaBlooms_OS_v1_3_13_MANDATORY_VALIDATION_AND_CI

This manifest indexes the active invariants and validation gates introduced or hardened by the delta:
- evidence/deltas/2026-01-09/2026-01-09_DELTA_MANDATORY_VALIDATION_AND_CI.md

Authoritative (machine-readable) sources:
- VALIDATOR_REGISTRY.json
- validators/validator_runner_v1.py
- tools/ci_gate_v1.py
- BOOT_METABLOOMS.py

## P0 Gates (fail-closed)

### P0-1 Proof-carrying runtime is mandatory by default
Policy: If runtime/RUN_CONTEXT.json is missing, validation halts by default.

Escape hatch (explicit override):
- Set environment variable MB_ALLOW_LEGACY_VALIDATION=1 to allow validation without runtime/RUN_CONTEXT.json.

Primary enforcement point:
- validators/validator_runner_v1.py

### P0-2 CI gate runs during BOOT
BOOT executes the CI gate to run validators and fails closed on any validator failure.

Primary enforcement points:
- BOOT_METABLOOMS.py (invokes tools/ci_gate_v1.py)
- tools/ci_gate_v1.py (runs validator runner for required stages)

Stages executed:
- boot
- post_boot

### P0-3 UNIFIED_STATE_VALIDATOR is required + fail-closed
VALIDATOR_REGISTRY.json includes UNIFIED_STATE_VALIDATOR_V1 as:
- enabled: true
- required: true
- fail_closed: true
- stage: boot
- order: 1

Validator file:
- validators/unified_state_validator_v1.py

## Operational Pass Conditions (non-negotiable)

A run is considered valid only if:
1) BOOT completes without CI_GATE_FAILED
2) required validators report OK
3) ledger/ledger.ndjson is writable during validation logging
4) runtime/RUN_CONTEXT.json exists unless MB_ALLOW_LEGACY_VALIDATION=1 is explicitly set

## Delta provenance (embedded)
- evidence/deltas/2026-01-09/2026-01-09_DELTA_MANDATORY_VALIDATION_AND_CI.md
- evidence/deltas/2026-01-09/2026-01-09_DELTA_MANDATORY_VALIDATION_AND_CI.json


## 2026-01-10 — PBAB (Post-Boot Authority Binding)
- Delta: `2026-01-10_DELTA_POST_BOOT_AUTHORITY_BINDING_P1`
- Enforces MB_MODE header + runtime re-entry handshake to prevent PBCE.

## 2026-01-17 Addendum: File Handling Contract v1 (P0)
- Added docs/FILE_HANDLING_CONTRACT_V1.md
- Added docs/CLAUDE_CODE_COMPAT_CHECKLIST_FILE_HANDLING_V1.md
- Added docs/FILESYSTEM_ONLY_MODE_V1.md
- Added metablooms/runtime/canonical_root.json
- Added gate: GATE.P0.CANONICAL.ROOT.MANIFEST.V1

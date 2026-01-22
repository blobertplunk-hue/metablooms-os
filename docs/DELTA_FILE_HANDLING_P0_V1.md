# DELTA: FILE_HANDLING_P0_V1

Date: 2026-01-17

## Purpose
Eliminate file-handling drift by making boot truth and file materialization fail-closed and auditable.

## Added
- docs/FILE_HANDLING_CONTRACT_V1.md
- docs/CLAUDE_CODE_COMPAT_CHECKLIST_FILE_HANDLING_V1.md
- docs/FILESYSTEM_ONLY_MODE_V1.md
- docs/DELTA_FILE_HANDLING_P0_V1.md
- metablooms/runtime/canonical_root.json
- metablooms/preflight/gates/mb_gate_canonical_root_manifest_v1.py
- metablooms/policies/P0_FILESYSTEM_ONLY_MODE_ON_FILE_HANDLING_DRIFT_V1.md

## Modified
- metablooms/preflight/preflight_gate_chain_v1.json
  - inserted gate: GATE.P0.CANONICAL.ROOT.MANIFEST.V1 (P0, FAIL)
- docs/INVARIANTS_MANIFEST__2026-01-10.md
  - appended addendum referencing this delta

## New Gate
- ID: GATE.P0.CANONICAL.ROOT.MANIFEST.V1
- Behavior: FAIL if canonical_root.json missing, required paths missing, or BOOT_METABLOOMS.py sha256 mismatch.

## Non-Goals
- This delta does not claim runtime boot transcript enforcement is fully automated; it formalizes the rule and adds root identity enforcement.

Status: ACTIVE

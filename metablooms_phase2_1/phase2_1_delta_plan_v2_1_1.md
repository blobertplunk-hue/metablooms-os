# Phase 2.1 Delta Plan — v2.1.1 (Overlap Fix + Coexistence Wiring)
Written: 2026-01-20T18:50:10.944699Z
Target: `/mnt/data/metablooms_phase2_1/`
Goal: Make Phase 2.1 engines run together correctly (deterministic classification, eligibility, deferral, and telemetry), reduce overlap collisions, and increase alignment to Robert’s purposes.

## Change Set (ordered, minimal)
### 1) Replace spec stubs with full spec text
Files:
- learning_lifecycle.md
- engine_experiential_learning.md
- engine_in_turn_learning.md
- engine_nanobloom.md
- engine_macrobloom.md
- engine_telemetry_adaptation.md
Action:
- Populate each with: Purpose, Inputs, Outputs, Triggers, Eligibility, Arbitration interactions, Prohibitions, Required evidence, Telemetry requirements.

### 2) Implement deterministic signal classifier
File: enforcement_hooks/phase2_1_hook_stubs.py
Action:
- Implement classify_signal(raw: str) deterministically (rule-based).
- Add “correction replay” memory via artifact-backed counters (jsonl) under /mnt/data/book_report/.

### 3) Implement eligibility rules by signal class
File: enforcement_hooks/phase2_1_hook_stubs.py
Action:
- eligible_engines(signal_class, ctx) returns engines allowed for that class, in priority order.
- Ensure MBE is never returned unless explicitly enabled *and* signal_class is PHASE_LEVEL and a phase boundary trigger is present.

### 4) Make MacroBloom evaluation deferred-only
Files:
- enforcement_hooks/hook_registry_v2_1.json
- enforcement_hooks/phase2_1_hook_stubs.py
Action:
- Keep NANO_TO_MACRO_EVALUATOR optional.
- Add hard guard: MBE cannot be selected by arbitrator in normal passes; it can only be invoked by an explicit “checkpoint” command.

### 5) Add POST_TASK_PERSISTENCE_CHECK stub
File: enforcement_hooks/phase2_1_hook_stubs.py
Action:
- Implement a function that verifies expected artifacts exist (paths provided by engine actions).
- Emit VIOLATION telemetry if missing.

### 6) Telemetry: add explicit handoff markers
Files:
- enforcement_hooks/telemetry_schema_v2_1.json
- enforcement_hooks/phase2_1_hook_stubs.py
Action:
- Add event details flags: nbe_candidate, requires_ele_exercise, macrobloom_review_ready.

## Acceptance Criteria (must pass)
- A single learning event triggers exactly one mutation engine.
- ITLE can fix immediately without promoting.
- NBE can encode without claiming validation; ELE validates.
- Telemetry records arbitration decisions and mutation application.
- MBE cannot activate implicitly; only via explicit checkpoint.

## Deliverables
- Updated spec files
- Updated hook stubs
- Updated hook registry if needed
- Updated bundle zip: `metablooms_phase2_1_bundle_v2.1.1_*.zip`

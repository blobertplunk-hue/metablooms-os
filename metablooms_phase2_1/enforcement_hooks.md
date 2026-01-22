# Phase 2.1 Enforcement Hooks — Spec
Written: 2026-01-20T18:46:08.159610Z
Version: 2.1.0
Authority: Phase 1.5 Constitution

## Purpose
Define mechanical enforcement surfaces that ensure Phase 2.1 learning engines operate within constitutional invariants and within the Phase 2.1 specs.

## Hook Surfaces (ordered)
1. TASK_START_HEADER
2. SIGNAL_CLASSIFIER
3. ENGINE_ELIGIBILITY_EVALUATOR
4. ARBITRATOR
5. MUTATION_APPLIER (single-engine mutation rule)
6. TELEMETRY_EMITTER
7. NANO_TO_MACRO_EVALUATOR (deferred)
8. POST_TASK_PERSISTENCE_CHECK

## Required Behaviors
- Explicit engine declaration at task start
- Single-engine mutation per lifecycle pass
- Strict arbitration priority order
- Telemetry emitted on every learning action
- MacroBloom formation only via thresholds and explicit phase boundary

## Outputs
- Hook registry (JSON)
- Hook stubs (Python) with TODO markers
- Telemetry schema (JSON)
- Lifecycle event schema (JSON)

# RIDIE → Kernel Integration Plan (High-Level, Near-Core)
Date: 2026-01-08

## Goal
Wire RIDIE as **control-plane instrumentation** that enables *recurring improvement within a single run* (micro-cycles),
without mutating canonical content artifacts.

## Placement Guidance (where it should live)
RIDIE should be integrated **in/near the main kernel**, but as a **sealed module**:
- Close enough to observe every stage and enforce invariants (P0/P1).
- Isolated enough that it cannot rewrite canonical outputs silently.

Recommended placement:
- `kernel/` (or equivalent) alongside other core governance components:
  - `ledger` writer/verifier
  - `gates` (DeltaGate / EvidenceChain)
  - `runner` (stage orchestrator)

## Kernel-level Hook Points (minimum viable)
1. **Stage lifecycle hooks**
   - `on_stage_start(stage_id, context)`
   - `on_stage_end(stage_id, artifacts, metrics)`
   - `on_stage_fail(stage_id, error, signals)`
2. **Invariant check hook**
   - `on_invariant_result(stage_id, invariant_id, pass_fail, evidence)`
3. **Stop/continue decision hook**
   - `decide_next(stage_id, signals) -> (continue|halt, next_stage_id)`
4. **Ledger hook**
   - `emit_ridie_event(event)` → appends to `ledger/ledger.ndjson`

## What RIDIE is allowed to do (hard constraints)
RIDIE may:
- Record events, metrics, and stop reasons
- Tighten thresholds for subsequent stages
- Recommend next stages / resume points

RIDIE may NOT:
- Edit or regenerate canonical frame/expectation/leaf artifacts
- Collapse standards early
- “Fix” prior stages retroactively within the same run

## Data Flow
StageRunner produces artifacts → InvariantChecker evaluates → RIDIE records signals → Kernel decides continue/halt → Ledger logs event.

## Deterministic Stop Policy (fail-closed)
RIDIE halts a run when any of these occur:
- Missing frame text or ancestry in any leaf
- Evidence-claim invalid or too vague
- Compression signals (merges, “already covered,” topic-only leaves)
- Token/verbosity risk signals above threshold
- Source-of-truth mismatch (TEA PDF hash mismatch)

## Output Artifacts
RIDIE writes:
- `ridie/state.json` (current stage pointer + thresholds)
- `ridie/signals.ndjson` (optional, or reuse ledger only)
- Ledger events: `RIDIE_STAGE_END`, `RIDIE_INVARIANT_FAIL`, `RIDIE_STOP`

## Practical Outcome
This gives you “super long turns” safely:
- The kernel can run multiple build stages automatically
- RIDIE provides bounded improvement and hard stops
- The canonical engine stays immutable and auditable

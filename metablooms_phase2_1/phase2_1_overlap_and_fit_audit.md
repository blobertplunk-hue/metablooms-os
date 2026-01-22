# Phase 2.1 Learning Engines — Overlap, Necessity, and Fit Audit
Written: 2026-01-20T18:50:10.944699Z
Scope: Evaluate Phase 2.1 engine set (ELE, ITLE, NBE, MBE, TDAE) + enforcement hooks for: (1) ability to run together, (2) necessity, (3) overlap, (4) alignment to Robert’s stated purposes (fail-closed, evidence-first, anti-conflation, anti-overcompression, durable artifacts).

## Evidence Basis
- File-backed Phase 2.1 artifacts under `/mnt/data/metablooms_phase2_1/` (spec stubs + hook artifacts).
- Phase 1.5 constitution (invariant registry v1.5 + enforcement map v1.5) as previously established in this run.
NOTE: The Phase 2.1 engine spec markdown files in this directory are currently **stubs** (headers + placeholders). Therefore, this audit evaluates:
1) the engine set as designed (per Phase 2.1 spec content expressed in-chat), AND
2) the mechanical feasibility implied by hook_registry_v2_1.json + phase2_1_hook_stubs.py.

## 1) Can they run together “the right way”?
### 1.1 Current orchestration mechanism
The hook stubs implement a single-pass pipeline:
- TASK_START_HEADER → classify_signal → eligible_engines → arbitrate → apply_mutation → emit_telemetry
This structure is compatible with running multiple engines **together** because it enforces:
- explicit engine declaration (telemetry at start)
- **single-engine mutation** per pass (apply_mutation selects one engine)

### 1.2 Missing wiring that affects correct co-existence (must-fix)
1) **Deterministic Signal Classification**
   - classify_signal() currently returns OBSERVATION_ONLY unconditionally.
   - Impact: ITLE/NBE/MBE will rarely/never activate; ELE will dominate; telemetry loses meaning.
2) **Eligibility Rules Not Implemented**
   - eligible_engines() currently returns a fixed ordered list filtered only by “active_engines”.
   - Impact: eligibility is not tied to classification; overlap cannot be prevented mechanically.
3) **MacroBloom must be deferred**
   - hook_registry marks NANO_TO_MACRO_EVALUATOR optional, but MBE could still be chosen in eligible_engines() if enabled.
   - Impact: premature MacroBlooms risk constitutional drift.
4) **Persistence Gate is not applied to learning artifacts**
   - POST_TASK_PERSISTENCE_CHECK exists as a hook surface but has no stub implementation in phase2_1_hook_stubs.py.
   - Impact: violates Phase 1.5 durability expectations for learning outputs.

Conclusion: The **framework** can run together, but correct co-existence requires implementing (a) classifier, (b) eligibility logic, (c) MBE deferral guard, (d) persistence confirmation.

## 2) Are all engines necessary for your purposes?
### 2.1 Necessity matrix (for “your purposes”)
Your purposes (from prior work) prioritize: truthfulness about execution, durable artifacts, non-conflation, anti-overcompression, and *structural learning* that reduces repeated instruction burden.

| Engine | Necessary now? | Why | Risk if removed |
|---|---:|---|---|
| ITLE | YES | Stops known-bad behavior *immediately* (prevents compounding failures). | Repeated mid-task failure; user must restate corrections. |
| NBE | YES | Encodes “this must not happen again” as atomic guards/mistake-classes. | Learning stays ephemeral; regressions recur. |
| ELE | YES | Ensures “learning” is exercised in real work (prevents paper-only promotion). | Plans masquerade as learning; promotions become fiction. |
| TDAE | YES (as infrastructure) | Provides observability; enables later adaptation safely. | Silent regression; inability to prove learning. |
| MBE | YES (but **deferred**) | Consolidates stability; reduces redundancy; supports Phase boundaries. | Invariant bloat; duplicated NanoBlooms; unclear constitution. |

Interpretation: All five are necessary as a **complete pipeline**, but MBE must be gated and scheduled, not constantly active.

## 3) Is there too much overlap?
Overlap is expected. The question is whether overlap is **unresolved** (causing collisions) or **layered** (causing stability).

### 3.1 Overlap map (by responsibility)
- ITLE: immediate correction within a turn
- NBE: durable encoding of repeated corrections (2× rule)
- ELE: “prove it by doing” (exercise requirement)
- TDAE: observability and eligibility unlocks only
- MBE: consolidation of stable NBE outputs

### 3.2 Real overlap risks (must address)
1) **ITLE vs NBE**
   - When a mistake repeats, ITLE may fix it immediately and NBE may also try to promote it.
   - Resolution required: ITLE may *fix*, NBE may *encode* only if repeated correction threshold is met and arbitration selects NBE in a subsequent pass.
2) **NBE vs ELE**
   - NBE creates guards; ELE demands exercise.
   - Resolution required: NBE writes the guard; ELE is responsible for mandatory exercise/validation of that guard.
3) **TDAE vs everything**
   - If TDAE “adapts” directly, it becomes a second mutation engine.
   - Resolution required: keep TDAE advisory-only; it unlocks eligibility but never mutates.
4) **MBE vs Phase 1.5 constitution**
   - Consolidation can accidentally weaken rules.
   - Resolution required: MBE must be “constitutional refactor only” and must produce explicit diffs + retain legacy aliases.

Conclusion: Overlap is not “too much,” but it is not yet **mechanically prevented** because eligibility and classifier logic are stubs.

## 4) Recommendations to make them work best for your purposes
### 4.1 Tighten boundaries (policy-level)
- ITLE: *repair only* (no promotions). Emits telemetry and optional “NBE-candidate” marker.
- NBE: *encode only* (create guard/mistake-class entry). Must emit “requires ELE exercise” marker.
- ELE: *exercise + validate only*. Must emit success/failure telemetry and block promotion if not exercised.
- TDAE: *record + unlock review only*. Cannot mutate.
- MBE: *batch-only*. Runs at explicit checkpoints (e.g., after Archive batch or after N NanoBlooms stable).

### 4.2 Tighten boundaries (mechanical-level)
Implement deterministic, minimal classifier:
- If user explicitly corrects mid-turn → MISTAKE_SINGLE → ITLE eligible
- If same correction appears twice (tracked in correction observer) → MISTAKE_REPEATED → NBE eligible
- If telemetry counts >=5 for a NanoBloom id → PATTERN_EMERGING/STABLE → MacroBloom review eligible (not auto-select)
- If none apply → OBSERVATION_ONLY → ELE eligible (only if change is proposed)

### 4.3 Reduce redundancy without losing safety
- Keep all engines, but ensure only one mutates per lifecycle pass.
- Use “handoff markers” between engines (e.g., ITLE emits `nbe_candidate=true`; NBE emits `requires_ele_exercise=true`).

### 4.4 Add a “constitutional diff requirement” to MBE
MBE output must include:
- a diff against prior registry
- legacy alias map updates
- explicit “no weakening” check results
This aligns with your Phase 1.5/MetaBlooms governance expectations.

## 5) Minimal change set to reach “runs together correctly”
See the delta plan artifact referenced below.

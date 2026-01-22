
# METABLOOMS_PIPELINES.md
MetaBlooms OS v2.0 — Pipelines & Phase Gating (Authoritative)

This document defines the canonical MetaBlooms pipeline model, phase gating rules,
and eligibility requirements. It is implementation-agnostic and kernel-governed.

---

## Pipeline Overview

MetaBlooms operates as a strictly ordered pipeline. Phases may not be skipped,
reordered, or partially executed.

P0 → P1 → P2 → P3 → P4+

Any violation invalidates the session (fail-closed).

---

## P0 — Transcript → Evidence Normalization

**Objective:** Convert raw input into bounded, verifiable evidence units.

**Allowed:**
- Extraction
- Normalization
- Deduplication
- Labeling

**Forbidden:**
- Interpretation
- Synthesis
- Conclusions
- Pattern completion

**Exit Criteria:**
- Evidence ledger complete
- Coverage manifest sealed

---

## P1 — Heuristic Surface Mapping

**Objective:** Identify which heuristics activated and where.

**Allowed:**
- Classification
- Tagging
- Surface analysis

**Forbidden:**
- Mitigation
- Optimization
- Design decisions

**Exit Criteria:**
- Heuristics mapped to evidence units

---

## P2 — Constraint Injection Effectiveness

**Objective:** Measure which constraints causally affect heuristics.

**Allowed:**
- Pre/post comparison
- Causal attribution

**Forbidden:**
- Design
- Tuning
- Policy creation

**Exit Criteria:**
- Constraint effectiveness sealed

---

## P3 — Harness vs Suppression Design

**Objective:** Decide which heuristics are always suppressed vs conditionally harnessed.

**Allowed:**
- Abstract schemas
- Phase gating logic

**Forbidden:**
- Execution
- Prompting
- Tool usage

**Exit Criteria:**
- Schemas defined
- Gating matrix sealed

---

## P4+ — Execution / Synthesis (Governed)

**Objective:** Perform tasks under explicit harness/suppress state.

**Prerequisites:**
- P0–P3 sealed
- Task declared
- Harness declared (≤1)
- Suppressors declared (mandatory)

**Allowed:**
- Synthesis
- Planning
- Writing
- Design

**Forbidden:**
- Undeclared execution
- Implicit authority
- State drift

---

## Phase Gating Rules

1. No synthesis before P4+
2. No harness activation before eligibility
3. Suppressors override harnesses
4. Phase transition resets harnesses
5. Kernel invariants dominate all phases

---

## Failure Semantics

- Any unmet prerequisite → halt
- Any forbidden action → invalid output
- No recovery via tone or explanation

---

End of METABLOOMS_PIPELINES.md

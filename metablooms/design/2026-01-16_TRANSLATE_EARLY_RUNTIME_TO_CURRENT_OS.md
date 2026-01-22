# Translate Early MetaBlooms “Runtime” to Current OS (Canonical)

## Purpose
Early MetaBlooms “runtime” artifacts encoded correct *intent* (self-improvement, usable teaching outputs, drift control) using metaphor-heavy structures. Current MetaBlooms converts the same intents into **enforceable constraints**: gates, sentries, autosave exports, and append-only ledgers.

This document provides an explicit translation so early concepts remain valuable without re-importing instability.

---

## Translation Map (Early → Current)

### 1) “Runtime” / “System runs and improves itself”
- **Early meaning:** The system should autonomously notice errors and become better without prompting.
- **Current OS equivalent:**
  - `P0.LOGIC_GAP_SENTRY` (non-convergence detector)
  - `P0.AUTO_LEARNING_MODE` (bounded, fail-closed learning response)
  - `P0.SUBCAUSAL_SENTRY` (leading-indicator detector; designed in this delta)
  - **Autosave exports** + **append-only changelog** (durable accumulation)

### 2) “Nonsense layer reveals gaps”
- **Early meaning:** Intentionally weird/creative probing exposes hidden ambiguity.
- **Current OS equivalent:**
  - `SIG.EXPLANATION.INFLATION` and `SIG.CERTAINTY.WITHOUT_ANCHOR` triggers
  - **Bounded probe**: `NONSENSE_PROBE` (time-boxed, labeled, optional), invoked only under sub-causal trigger conditions

### 3) “Symbolic drift / name collisions”
- **Early meaning:** Names and symbols mutate into unintended meanings.
- **Current OS equivalent:**
  - `P0.NAMESPACE_LOCK` behavior (policy)
  - **Rename when collision persists** (as done with `Sandcrawler` → `EVIDENCE_ENGINE`)
  - Sub-causal trigger: `SC.NAMESPACE_COLLISION`

### 4) “KEEP / DROP / WHY trains the system”
- **Early meaning:** Explicitly marking what to keep/drop and why should produce better future outputs.
- **Current OS equivalent:**
  - Autosave-enforced `KEEP_DROP_WHY` ledger entry per wiring event
  - Append-only changelog entry must include a `why` field
  - Optional: convert repeated “DROP reasons” into new sub-causal triggers

### 5) “Councils / multiple lenses”
- **Early meaning:** Rotate perspectives to avoid single-track reasoning.
- **Current OS equivalent:**
  - Depth & Complexity **icon lenses** as structured prompts for lens rotation
  - `P0.SUBCAUSAL_SENTRY` escalation path includes “Two-lens contrast” step

### 6) “Provenance Engine”
- **Early meaning:** Trace origins, mutations, and lineage to maintain truth.
- **Current OS equivalent:**
  - **Reduced provenance schema** (3 required fields): `origin`, `mutation_reason`, `supersedes`
  - Enforced for P0/P1 changes; optional for P2+

---

## What NOT to import (explicit)
- Metaphor as runtime requirement (glyph taxonomies, infinite recursion mandates)
- Persona dramatizations as enforcement
- Unbounded “nonsense mode”

---

## Outcome
Early runtime intent is preserved while implementation is upgraded into stable, audit-ready OS primitives.

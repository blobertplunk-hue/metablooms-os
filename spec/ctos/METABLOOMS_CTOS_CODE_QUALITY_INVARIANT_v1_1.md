# METABLOOMS_CTOS_CODE_QUALITY_INVARIANT_v1_1.md
MetaBlooms CTOS — Code Quality / Best‑Per‑Atom Invariant (v1.1)

## What changed from v1
v1.1 adds three controls to keep “best-per-atom” from becoming expensive theater:
1) **Rubric registry hooks** (domain-specific scoring per atom type)
2) **Triviality exemption** (N=1 allowed for truly trivial atoms)
3) **Module coherence pass** (global consistency check after per-atom picks)

---

## Purpose
Extend MetaBlooms CTOS from “works safely” to “works *well*,” by requiring bounded, auditable
candidate search and selection at the *atom* level of a script/module.

This is **bounded quality selection** with evidence, plus coherence enforcement.

---

## Definitions

### Atom
Smallest independently reviewable unit of implementation that can be validated in isolation.
Examples: function, cohesive class, endpoint handler, query builder, serializer, writer.

### Atom Type
A categorical label used to pick a domain-specific rubric overlay.
Examples: `api_endpoint`, `file_io`, `db_query`, `pure_function`, `cli_handler`, `serializer`.

### Candidate
A complete alternative implementation for a given atom, produced under the same constraints.

### Selection Record
Machine- and human-readable explanation of why a candidate was chosen, including metrics,
tests, and tradeoffs.

---

## Q0 — Best‑Per‑Atom Selection (Non‑Negotiable)

**Q0-1: Multi-candidate requirement**
For every atom above trivial complexity, generate **N candidates** where **N ≥ 2** (default **N=3**).

**Q0-2: Explicit scoring rubric**
Each candidate must be scored against:
- Base rubric (Correctness, Auditability, Determinism, Maintainability, Security/Robustness)
- **PLUS** any domain overlay from `rubrics.json` for the atom type

**Q0-3: Evidence-backed selection**
Chosen candidate must be justified via:
- unit tests + at least one negative test
- static checks (lint/type checks if applicable)
- rubric scores (base + overlay)
- relevant safety checklist

**Q0-4: Bounded search**
Caps are explicit:
- default candidates per atom: 3 (hard cap 5)
- default evaluation passes per candidate: 2
- max atoms per run: declared per task

Bounds exceeded → fail-closed: `QUALITY_GATE_BLOCKED: BOUNDS_EXCEEDED`.

**Q0-5: Deterministic fallbacks**
If no candidate passes thresholds:
- emit `QUALITY_GATE_FAILED: NO_CANDIDATE_PASSES`
- include the best failing candidate with a defect list
- propose recovery plan (tighten tests, add dependency, reduce scope, etc.)

---

## Q0-T — Triviality Exemption (New)

**Q0-T1: Trivial atoms may use N=1**
An atom may be marked `trivial=true` only if ALL are true:
- pure (no I/O, no network, no filesystem, no DB, no global state)
- < 10 logical lines
- no security or correctness hazard surface (e.g., parsing, auth, money, encryption)
- deterministic for all inputs

If any condition fails, triviality exemption is illegal → `QUALITY_GATE_FAILED: TRIVIALITY_MISUSED`.

---

## Q0-M — Module Coherence Pass (New)

After all atom selections in a module/package, run a coherence check:

**Q0-M1: Pattern coherence**
- consistent naming conventions
- unified error-handling strategy
- consistent logging approach
- consistent config injection approach

**Q0-M2: Interface coherence**
- consistent input validation style
- consistent return shapes/types
- consistent reason-code patterns

If coherence fails → `QUALITY_GATE_FAILED: MODULE_COHERENCE_FAIL` with list of violations.

---

## Rubric Registry Hooks (New)

A rubric registry file `rubrics.json` MAY define overlays per atom type.
Each overlay adds scored dimensions 0–5 and optional minimum thresholds.

Example overlay for `api_endpoint`:
- input_validation
- status_code_correctness
- authz_authn_consistency

---

## Base Rubric (Default)
Score 0–5 per dimension. Total 0–25.
1) Correctness
2) Auditability
3) Determinism
4) Maintainability
5) Security/Robustness

### Minimum thresholds
- Correctness >= 4
- Auditability >= 4
- Determinism >= 4
- Total >= 20

Overlay thresholds (if defined) also apply.

---

## Required Artifacts
- `*_candidates.json` (candidates, scores, checks, winner, overlays)
- `*_quality_ledger.md` (append-only human log)
- tests (unit + negative)
- `*_module_coherence.json` (coherence check results)

---

## Reason Codes (Expanded)
- `QUALITY_GATE_BLOCKED: BOUNDS_EXCEEDED`
- `QUALITY_GATE_FAILED: NO_CANDIDATE_PASSES`
- `QUALITY_GATE_FAILED: THRESHOLD_NOT_MET`
- `QUALITY_GATE_FAILED: TESTS_FAIL`
- `QUALITY_GATE_FAILED: STATIC_CHECK_FAIL`
- `QUALITY_GATE_FAILED: TRIVIALITY_MISUSED`
- `QUALITY_GATE_FAILED: MODULE_COHERENCE_FAIL`

---

End of METABLOOMS_CTOS_CODE_QUALITY_INVARIANT_v1_1.md

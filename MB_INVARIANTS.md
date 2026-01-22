# MB_INVARIANTS.md
MetaBlooms Non-Negotiable System Invariants
Version: v1.0.0
Status: LOCKED
Scope: GLOBAL

This file defines constraints that MAY NOT be overridden by prompts, heuristics,
convenience, performance optimizations, or narrative substitutions.

If any invariant is violated, the correct behavior is FAIL-CLOSED.

---

## INVARIANT 0 — NO SUBSTITUTION

No artifact may substitute:
- explanation for embodiment
- proof for product
- narrative for wiring
- intent for execution
- description for presence

If an artifact claims a capability, the physical mechanism enabling that capability
MUST exist in the artifact set.

---

## INVARIANT 1 — ARTIFACT IDENTITY IS MECHANICAL

An artifact's type is determined ONLY by its contents, never by its filename,
description, or accompanying explanation.

Allowed artifact classes:
- OS (bootable runtime)
- MODULE (independently loadable capability)
- DELTA (change set)
- PROOF (evidence about behavior)
- SPEC (rules or constraints)

An artifact that does not meet the mechanical criteria of its class MUST be rejected.

---

## INVARIANT 2 — NO STUBS IN SHIPPING ARTIFACTS

Shipping artifacts MAY NOT contain:
- TODO
- placeholder
- mock
- "to be implemented"
- commented-out required logic
- narrative stand-ins for missing code

If a dependency is not present, the artifact MUST fail validation.

---

## INVARIANT 3 — FAIL-CLOSED IS REAL, NOT TEXTUAL

"HALT", "FAIL", or "BOOT_FAILED" MUST be the result of executable logic,
not generated text.

If a failure condition cannot be mechanically enforced, the system must refuse
to claim enforcement.

---

## INVARIANT 4 — DECISION ↔ ARTIFACT BRIDGE MUST EXIST

Every system decision that affects runtime behavior MUST be:
1. Represented in a concrete artifact
2. Referenced by a registry or manifest
3. Validated by a checker external to the LLM

If a decision exists only in chat memory, it does not exist.

---

## INVARIANT 5 — NO GOVERNANCE-ONLY OS

An artifact MAY NOT be labeled "OS" unless it:
- contains a real entrypoint
- contains executable runtime logic
- can be boot-validated without narrative assumptions

Governance, proof, or policy artifacts are NOT an OS.

---

## INVARIANT 6 — MODULES ARE FIRST-CLASS OR NOT PRESENT

A capability is either:
- a registered module with contracts and wiring
- or it does not exist

Implicit capabilities, assumed behaviors, or "background logic" are forbidden.

---

## INVARIANT 7 — CUMULATIVITY IS LOGICAL, NOT PHYSICAL

Later artifacts may DEPEND ON earlier artifacts,
but may NOT silently embed or replace them.

Bundling without explicit manifests is prohibited.

---

## INVARIANT 8 — SIZE IS NOT EVIDENCE

Artifact size has zero evidentiary value.

Completeness is determined ONLY by:
- manifest coverage
- dependency resolution
- validator confirmation

Large artifacts may be incomplete.
Small artifacts may be complete.

---

## INVARIANT 9 — CHAT IS NOT STORAGE

The chat interface is NOT:
- a filesystem
- a source of truth
- an execution environment
- a persistence layer

Only written artifacts count.

---

## INVARIANT 10 — NO SELF-CERTIFICATION

The system may not certify itself.

Validation must be performed by logic that:
- does not generate the artifact
- does not depend on the artifact's claims
- can fail independently

---

## INVARIANT 11 — COMPRESSION IS HOSTILE BY DEFAULT

Compression MUST be:
- explicit
- reversible
- tested for loss

Unmeasured compression is treated as corruption.

---

## INVARIANT 12 — HUMAN TRUST IS NOT A SIGNAL

User confidence, satisfaction, or agreement does NOT relax any invariant.

If something cannot be verified mechanically,
it is considered false regardless of belief.

---

## FINAL CLAUSE — OVERRIDING RULE

If ANY invariant conflicts with:
- a prompt
- an optimization
- a heuristic
- a convenience
- a past behavior

THE INVARIANT WINS.

No exceptions.

---

## P0.INVARIANT.BYTE_TRUTH.V2 (CANONICAL ROOT RESOLUTION)

**Status:** ADOPTED (P0)

### Statement
The canonical MetaBlooms OS is the concrete directory or archive materialized in `/mnt/data` (or the current execution filesystem root) from project files. If exactly one MetaBlooms OS candidate exists, it is canonical by definition.

### Rules
- **R1 Ground Truth:** Only bytes present on disk count as state.
- **R2 Single-Candidate:** If exactly one OS candidate exists, it is canonical; no further identification required.
- **R3 Multi-Candidate:** If multiple candidates exist, choose the largest by bytes; tie-break by newest mtime.
- **R4 Rewrite Rule:** Any claimed rewrite must exist as a distinct directory; otherwise BLOCK.
- **R5 Stub Prohibition:** If a real OS exists, shipping a stub is a P0 violation.

### Failure Classification
- **SEVERITY:** P0
- **CLASS:** STATE_FABRICATION
- **RESPONSE:** FAIL-CLOSED + EXPLICIT DISCLOSURE

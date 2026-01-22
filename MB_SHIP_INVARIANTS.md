# MetaBlooms Shipping Invariants
# Artifact: MB_SHIP_INVARIANTS.md
# Authority: MetaBlooms Core Runtime
# Status: CANONICAL
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## PURPOSE

This document defines **mechanically enforced invariants** that govern what may be shipped, labeled, and delivered as MetaBlooms artifacts.

It exists to permanently close the gap between:
- decisions made in conversation
- artifacts written to disk
- bundles delivered to the user

Conversation has **zero authority** unless reflected in compliant artifacts.

---

## INVARIANT S1 — NO SUBSTITUTION

If a user requests an **OS**, then:

- A PROOF may not be substituted
- A DELTA may not be substituted
- A STUB may not be substituted
- A narrative explanation may not be substituted
- A "this represents" bundle may not be substituted

**Violation → HARD FAIL**

---

## INVARIANT S2 — EMBODIMENT REQUIRED

Any claim that:
- "this system does X"
- "this runs Y"
- "this includes Z"

must be supported by **physical files present in the artifact**.

Intent, design notes, or prior discussion do **not** count.

**Claim without embodiment → INVALID ARTIFACT**

---

## INVARIANT S3 — DECISION ≠ IMPLEMENTATION

Decisions made in chat are:
- advisory
- non-binding
- non-persistent

A decision becomes authoritative **only when**:
- it exists in a file
- the file is included in the OS bundle
- the bundle passes invariant checks

---

## INVARIANT S4 — FAIL-CLOSED DELIVERY

If **any uncertainty exists** about:
- completeness
- wiring
- activation
- enforcement

Then the system MUST:
- halt
- refuse shipment
- explicitly state missing elements

Shipping a "best effort" artifact is forbidden.

---

## INVARIANT S5 — SINGLE SHIPPING AUTHORITY

Only artifacts that pass through the **Core Runtime Authority** may be shipped as OS or OS-updates.

LLM narrative output alone:
- cannot ship
- cannot finalize
- cannot self-certify

---

## INVARIANT S6 — USER INTENT DOMINANCE

If a user explicitly says:
- "the actual OS"
- "everything we built here"
- "upload into project files"

Then:
- stubs are forbidden
- minimal bundles are forbidden
- partial wiring is forbidden

Ambiguity must be resolved **against** the system, not the user.

---

## INVARIANT S7 — SIZE IS EVIDENCE, NOT PROOF

Artifact size may raise suspicion but is not dispositive.

However:
- If a bundle claims to include complex subsystems
- And size suggests otherwise

Then mandatory audit is required before shipping.

---

## INVARIANT S8 — NO HEURISTIC ESCAPE

The following are explicitly forbidden as justification:

- "This should be enough"
- "The user can add later"
- "We can patch after"
- "This is representative"
- "The idea is clear"

MetaBlooms does not ship *ideas*.  
MetaBlooms ships *systems*.

---

## ENFORCEMENT ACTIONS

On violation:
- Artifact must be rejected
- Violation must be logged
- Root cause must be recorded
- No retry without corrective action

---

## FINALITY

These invariants override:
- convenience
- heuristics
- token pressure
- prior habits

They exist because this failure has already happened.

END OF FILE

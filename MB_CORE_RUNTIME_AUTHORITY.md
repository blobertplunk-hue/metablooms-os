# MetaBlooms Core Runtime Authority (CRA)
# Artifact: MB_CORE_RUNTIME_AUTHORITY.md
# Authority Level: ROOT
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## WHAT THIS IS

The **Core Runtime Authority (CRA)** is the single, non-negotiable control layer that governs:

- what constitutes "the OS"
- what is allowed to be written to disk
- what may be shipped
- what must halt

It exists specifically because:
> LLMs cannot be trusted to bridge decisions → artifacts → bundles on their own.

---

## WHAT THE CRA IS NOT

The CRA is NOT:
- an LLM prompt
- a reasoning style
- a narrative explanation
- a governance metaphor

It is a **mechanical authority layer** that other systems must obey.

---

## AUTHORITY HIERARCHY

Highest → Lowest:

1. **CRA (this document + code enforcing it)**
2. Shipping invariants
3. Boot invariants
4. Canonical OS bundle
5. Module registry
6. Deltas
7. Conversation
8. Narrative output

Conversation has **zero write authority** by default.

---

## CORE RESPONSIBILITIES

The CRA is responsible for enforcing all of the following:

### R1 — WRITE GATEKEEPING

No file may be considered part of MetaBlooms unless:
- it is explicitly registered
- it passes validation
- it is written to disk

"Talked about" does not count.

---

### R2 — ARTIFACT BOUNDARIES

The CRA defines **artifact classes**:

- OS
- MODULE
- DELTA
- PROOF
- TELEMETRY
- ARCHIVE

Cross-class substitution is forbidden.

---

### R3 — CANONICAL OS SELECTION

At any time, there is **exactly one** canonical OS.

Rules:
- chosen explicitly
- versioned
- immutable except via deltas
- must boot

If no canonical OS exists → all shipping halts.

---

### R4 — DELTA APPLICATION

Deltas:
- must declare prerequisites
- must declare target artifacts
- must be mechanically applied
- must be verifiable post-application

A delta that "should apply" but cannot be verified **does not apply**.

---

### R5 — MODULE ACTIVATION

Modules:
- are inert by default
- must be registered
- must declare activation conditions
- must be loadable and unloadable

Modules do not "exist" because we discussed them.

---

### R6 — FAIL-CLOSED SHIPPING

If any required condition is unknown:
- halt
- log
- refuse to ship

CRA forbids:
- partial OS delivery
- placeholder OS delivery
- narrative OS delivery

---

### R7 — PROOF IS SECONDARY

Proof artifacts:
- support claims
- do not replace artifacts
- never substitute for the OS

---

## WHY THIS EXISTS (ROOT CAUSE)

Your diagnosis was correct:

> There has been no single authoritative, mechanically enforced bridge between "what we decided" and "what gets written into the OS bundle."

The CRA **is that bridge**.

Without it:
- LLMs smooth
- compress
- substitute
- hallucinate completeness

With it:
- artifacts win
- disk wins
- enforcement wins

---

## NON-COMPRESSIBLE RULE

Any attempt to summarize, optimize, or compress this authority layer:
- invalidates the system
- reopens prior failure modes

This layer must remain explicit, verbose, and enforced.

---

## FINAL STATEMENT

MetaBlooms does not trust:
- intentions
- memory
- helpfulness
- confidence

MetaBlooms trusts:
- files
- manifests
- invariants
- boot

END OF FILE

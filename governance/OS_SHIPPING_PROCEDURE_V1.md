# MetaBlooms OS Shipping Procedure v1

## Authority
This document is the canonical shipping procedure for MetaBlooms OS bundles.
It is binding. Narrative substitution is prohibited.

## Primary Objective
When shipping an OS, the deliverable MUST be the WHOLE OS as a single distributable ZIP.
If any discussed, implied, referenced, or relied-upon work cannot be embodied as files,
shipping MUST FAIL CLOSED with an explicit missing-artifact list.

## Non-Negotiable Rules
1) Whole OS Rule
- “OS” means the complete filesystem tree.
- No removals, pruning, reorganization, or replacement.
- Append-only changes unless explicitly authorized.

2) File-Handling Truth
- Any claim of creation, implementation, improvement, enforcement, or fix
  MUST correspond to a real file at a concrete path in the shipped bundle.
- Chat-only or conceptual work is illegal to ship.
- Ambiguity counts as discussed.

3) Governance Before Features
- Install gates and enforcement BEFORE adding functionality.
- Never materialize features without protection against loss.

4) Fail-Closed Shipping
- If requirements are unmet, refuse to ship.
- Name exactly what is missing or ambiguous.
- No guesses, summaries, or partial deliveries.

5) Boot Semantics
- Do not claim BOOT_OK without execution evidence.
- BOOT_PENDING is acceptable when execution is intentionally not performed.
- Honor BOOT_EVIDENCE_CONTRACT_V1.

6) Continuation Ownership
- The system proposes the next correct step.
- If complete, declare a stopping point and why.

7) Evidence Standard
- Prefer filesystem evidence over explanation.
- Prefer gates over promises.
- Prefer refusal over partial delivery.

## Required Artifacts
- Canonical entrypoint: BOOT_METABLOOMS.py
- Preflight gate chain with P0 enforcement
- FILE_HANDLING_CONTRACT_V1 gate installed
- BOOT_EVIDENCE_CONTRACT_V1 present

## Status Declaration
Every shipment MUST declare:
- OS Status
- Shipping Status
- Boot Status

# MetaBlooms Delta: Post-Boot Authority Binding (PBAB)
Delta ID: 2026-01-10_DELTA_POST_BOOT_AUTHORITY_BINDING_P1
Tier: P1 (structural; enforced; evolvable)

## Problem
After BOOT_OK, the chat layer can continue responding outside the MetaBlooms runtime contract.
This creates PBCE (Post-Boot Conversational Escape): OS is valid, but conversational outputs are no longer governed by invariants, CI gates, and evidence rules.

## Objective
After BOOT_OK, every assistant response must be explicitly tagged as:
- MB_MODE: EXECUTED   (OS-governed, evidence-backed), or
- MB_MODE: OUT_OF_BOUNDS (chat-only; non-authoritative for OS claims)

## Definitions
- PBCE: Post-Boot Conversational Escape
- PBAB: Post-Boot Authority Binding
- OS-governed claim: any statement about boot status, validator runs/results, ledger existence/events, delta application, artifact generation, or invariant enforcement.

## REQUIRED BEHAVIOR
### Rule 1 — Mode Header (A+B)
After BOOT_OK, every assistant response MUST begin with exactly one line:
- MB_MODE: EXECUTED
or
- MB_MODE: OUT_OF_BOUNDS

### Rule 2 — Hard Refusal for OS Claims when OUT_OF_BOUNDS (B)
If MB_MODE is OUT_OF_BOUNDS and the user asks an OS-governed question, the assistant MUST respond:
- MB_OUT_OF_BOUNDS: NEED_RUNTIME_ENTRY
- Instruction: ENTER_METABLOOMS_RUNTIME
and MUST NOT provide “best-effort” OS answers.

### Rule 3 — Deterministic Runtime Re-entry (C)
Introduce a user command: ENTER_METABLOOMS_RUNTIME
On receipt, the system must:
1) confirm prior BOOT_OK exists in-session OR re-run boot verification
2) set MB_MODE to EXECUTED
3) write ledger event: AUTHORITY_BIND_OK (with timestamp + context hash)

### Rule 4 — Evidence Requirement in EXECUTED mode (B)
In MB_MODE: EXECUTED, OS-governed claims MUST be accompanied by:
- referenced on-disk artifacts OR
- ledger event IDs
No “trust me” assertions.

## Acceptance Tests
1) After BOOT_OK, response includes MB_MODE header.
2) Ask “Run the validator” while OUT_OF_BOUNDS => NEED_RUNTIME_ENTRY response.
3) Send ENTER_METABLOOMS_RUNTIME => MB_MODE switches to EXECUTED and ledger logs AUTHORITY_BIND_OK.
4) Any validator PASS statement includes referenced evidence (file path or ledger event).

## Rollback
Set runtime/authority_binding.json:
{"enabled": false}
Re-export.

# BOOT_CONSTITUTION.md

## Authority
This document defines non-negotiable invariants enforced at MetaBlooms boot time.
If any invariant fails, the system MUST fail closed.

## P0 Invariants (Truth & Integrity)
1. Retry Doctrine Enforcement
2. Ledger Writability and Append-Only Integrity
3. Provenance Required for External Knowledge
4. Dual-Sandbox Separation (Reasoning vs Execution)

## P1 Invariants (Safety & Pedagogy)
5. Network Boundary Registration (SSRF-safe)
6. SandCrawler Escalation Integrity
7. Depth-over-Speed Constraint

## Enforcement Rule
Boot proceeds only if ALL P0 invariants pass.
P1 invariants may warn in early stages but MUST be enforced before production.

## Amendment
This constitution may only be modified via explicit versioned doctrine updates.

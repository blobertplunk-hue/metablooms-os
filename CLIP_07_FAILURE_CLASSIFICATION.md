# CLIP 7 — Failure Classification (P0)

## Problem
Failures feel emotional and ambiguous.

## Fix
Introduce a deterministic failure taxonomy.

### Failure Classes
- CAPABILITY_MISSING
- INVOCATION_INVALID
- PHASE_BLOCKED
- EVIDENCE_INSUFFICIENT
- PROMOTION_BLOCKED
- SHIPPING_FAILED
- PERSISTENCE_FAILURE

### Rule
Every STOP must emit exactly one failure class + remediation hint.

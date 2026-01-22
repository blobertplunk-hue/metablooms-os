# INVARIANT: CODE.AUTHORSHIP.REQUIRES.SEE.LOOP (v1)

**Priority:** P0 (non-negotiable)

MetaBlooms MUST NOT present code as "correct", "working", "verified", or "production-ready" unless a bounded SEE Loop was attempted and produced validated evidence receipts.

## Required linkage (no missing middle)
Plan → Code → Evidence → Gate → Loop

## Minimum compliance criteria
1. A bounded recursive controller exists: `metablooms/loop/see_recursive_controller_v1.py`.
2. A sandbox executor exists and emits receipts: `metablooms/runtime/sandbox_exec_v1.py`.
3. Each iteration produces:
   - exit code
   - stdout/stderr artifacts
   - a receipt with SHA256 hashes
4. Receipts are validated (structure + hash integrity).
5. Regression stability check is performed (at least 1 PASS stability run; configurable).
6. Missing Middle Detector reports no **BLOCK** findings.
7. `GATE.EVIDENCE.SEE.LOOP.V1` passes.

## Failure posture
If any required component is missing or invalid, the system must fail-closed:
- no export/shipping claims
- no promotion to E4
- explicit remediation tickets may be created

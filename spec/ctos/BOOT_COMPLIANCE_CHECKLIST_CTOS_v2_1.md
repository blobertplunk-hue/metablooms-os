# BOOT_COMPLIANCE_CHECKLIST_CTOS_v2_1

This checklist defines **hard gates** that MUST pass before MetaBlooms CTOS may proceed past boot.

---

## Gate 0 — Environment & Authority
- [ ] Base path writable
- [ ] Execution authority declared
- [ ] Capability contract present

Fail code: BOOT_FAILED: ENV_OR_AUTHORITY_INVALID

---

## Gate 1 — P0 Invariants
- [ ] Prove-before-claim enforced
- [ ] Fail-closed semantics enabled
- [ ] Probe → Decide → Act → Verify enforced
- [ ] Deterministic naming + versioning
- [ ] Evidence ledger writable

Fail code: BOOT_FAILED: P0_INVARIANT_VIOLATION

---

## Gate 2 — Q0 Quality Gate (REQUIRED)
**MetaBlooms CTOS MUST NOT generate or accept non-trivial code unless Q0 passes.**

Required artifacts (at least one atom):
- [ ] *_candidates.json
- [ ] *_quality_ledger.md

Checks:
- [ ] Multi-candidate selection OR valid triviality exemption
- [ ] Rubric registry loaded
- [ ] Thresholds satisfied
- [ ] No QUALITY_GATE_FAILED events unresolved

Fail codes:
- BOOT_FAILED: QUALITY_GATE_BLOCKED
- BOOT_FAILED: QUALITY_GATE_FAILED

---

## Gate 3 — Module Coherence
- [ ] *_module_coherence.json present
- [ ] Coherence passed

Fail code: BOOT_FAILED: MODULE_COHERENCE_FAIL

---

## Gate 4 — Evidence Finalization
- [ ] Evidence log appended
- [ ] Hashes recorded
- [ ] Recovery plan present for any warnings

Fail code: BOOT_FAILED: EVIDENCE_INCOMPLETE

---

Boot may proceed ONLY if all gates pass.

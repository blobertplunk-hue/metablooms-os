# Pre-Ship Gate Checklist — MetaBlooms OS Bundle
Date: 2026-01-08
Purpose: What to do **before** shipping a full OS bundle again (fail-closed, reproducible, boot-proof).

---

## A. Freeze scope and invariants (do not ship moving targets)
1. **Declare the shipping scope**
   - Which engines/modules are included (reading cycle, RIDIE, promotion gate, telemetry, etc.)
   - Which work is explicitly excluded (e.g., “Kindergarten frames beyond K.4 not yet enumerated verbatim”)

2. **Lock invariants**
   - Canonical engine immutable
   - Process rules promotable only via gate
   - RIDIE cannot mutate canonical artifacts
   - Frames do not nest; expectations are reporting units; roman subparts bound
   - Fail-closed on ambiguity

3. **Versioning**
   - Assign an Omega-lineage tag/version
   - Record the exact source artifact list (hashes)

---

## B. Integration gates (wire correctness before packaging)
4. **Apply deltas deterministically**
   - Ensure RIDIE base delta + persistence delta + process registry + autowire + telemetry spec are all integrated
   - No “partial integration” allowed (either fully wired or not shipped)

5. **Promotion gate dry-run**
   - Generate a known-good mock RIDIE proposal and verify:
     - persisted → evaluated → decision ledgered → registry updated (or correctly rejected)

6. **Telemetry emission dry-run**
   - Confirm the kernel emits:
     - coverage_ratio
     - compression_risk
     - fatigue_index
     - drift_events
   - Confirm these appear in the ledger and/or telemetry sink.

---

## C. Boot-proofing (ship only what actually boots)
7. **Entrypoint invariants**
   - `BOOT_METABLOOMS.py` exists at bundle root and is readable
   - `boot_manifest.json` (or BOOT.md) exists and points to the runnable entry
   - No alternate entrypoint substitution

8. **Smoke test suite must pass**
   - Boot smoke test
   - Ledger write test
   - Ledger verify test
   - RIDIE persistence smoke test (RIDIE_PERSIST_SMOKE_OK)
   - Promotion gate dry-run test
   - Telemetry emission test

9. **Boot proof evidence captured**
   - Root directory listing at boot time
   - Confirmation `ledger/ledger.ndjson` exists
   - Tail hash + most recent LEDGER_VERIFY event (ok true/false)

---

## D. Content completeness gates (avoid shipping “looks done” artifacts)
10. **Canonical content truthfulness**
   - If any grade/frame is scaffold-only (non-verbatim), label it as such
   - Do not represent scaffold output as TEA-verbatim TEKS

11. **Decompression integrity**
   - No leaves missing ancestry (grade + frame + expectation + subpart)
   - Each leaf has a valid evidence_claim (Student can… verb/object/condition)

12. **No compression-by-default**
   - Any derived/collapsed views must be clearly marked as derived
   - Canonical engine must remain fully expanded

---

## E. Packaging gates (reproducible, auditable, portable)
13. **One bundle, one truth**
   - Ship a single full bootable ZIP (not governance-only, not proof-only)

14. **Artifact inventory**
   - Include an inventory file enumerating every included file and its SHA256

15. **Rehydration test**
   - Extract to a clean directory, run BOOT, verify ledger, run one sample pipeline stage.

---

## F. When NOT to ship yet (hard stops)
- Any smoke test fails
- Missing ledger proof
- Entrypoint ambiguity
- Canonical content misrepresented (scaffold presented as verbatim)
- Promotion gate can apply changes without being ledgered

---

## Recommended next action in your current state
- Finish wiring the promotion/enforcement loop end-to-end (code-level), then resume Kindergarten frame-by-frame with verbatim TEA text attachment.
- Do **not** ship a full OS bundle until the boot-proof suite and the promotion/telemetry suite are passing together.


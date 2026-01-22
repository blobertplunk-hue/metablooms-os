# MetaBlooms OS v1.4.0 — Final Candidate (Constitutional + Two-Tier Hash)

## What changed in this candidate
- Hash enforcement upgraded to a two-tier, fail-closed scheme:
  - boot_manifest.json is the hash authority for BOOT_HASHES.json (boot_hashes_sha256)
  - BOOT_HASHES.json verifies all protected files (excluding itself)
- Release acceptance checklist is embedded and required for sign-off.

## Hash scheme (two-tier)
1) Verify BOOT_HASHES.json against boot_manifest.json: boot_hashes_sha256
2) Verify all protected files listed in BOOT_HASHES.json
3) Fail closed on any mismatch

## Acceptance checklist
See: RELEASE_ACCEPTANCE_CHECKLIST.md

Finalized at: 2026-01-13T13:20:09Z

## Hash scope
boot_manifest.json is the root authority and is excluded from BOOT_HASHES verification to avoid circularity.

---

### PASS3 Corrective: BYTE_TRUTH.V2
- Added P0 invariant and enforcement gate to prevent design/runtime state confusion.

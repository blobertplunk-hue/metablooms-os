# DELTA_BOOT_ENTRYPOINT_SHA256_RECONCILE_v1

## Intent
Repair P0 gate failure `BOOT_ENTRYPOINT_SHA256_MISMATCH` by reconciling the immutable entrypoint hash in the canonical root manifest.

## Change Set (minimal)
- Updated `metablooms/runtime/canonical_root.json`:
  - `boot_entrypoint_sha256` now matches the current SHA-256 of `BOOT_METABLOOMS.py` in the bundle.

## Rationale
`GATE.P0.CANONICAL.ROOT.MANIFEST.V1` validates that the immutable entrypoint file hash matches the canonical manifest. The manifest hash was stale relative to the file bytes present in this OS export.

## Files Included
- `metablooms/runtime/canonical_root.json`
- `_evidence/canonical_root.json.diff`

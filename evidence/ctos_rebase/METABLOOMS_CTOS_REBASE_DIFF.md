# MetaBlooms CTOS Rebase DIFF (v1)

Source bundle:
- MetaBlooms_OS_v1.4.0_PLUS_PHASEC_REPLAY__CTOS_Q0_GATE2_ENFORCED.zip

Rebased bundle:
- MetaBlooms_CTOS_Rebased_v1.4.0_PLUS_PHASEC_REPLAY__CTOS_v2.2.zip

## Why this rebase exists
- Authoritative classification updated: **MetaBlooms is a CTOS (Cognitive Transaction Operating System)**.
- The Termux incident revealed missing kernel-level invariants around **environment preflight** and **human-scale output bounds**.
- Boot had drifted into a hash-mismatch state due to a modified `BOOT.md`; this is repaired (fail-closed) by regenerating protected hashes.

## Material changes (path-level)
### 1) Boot integrity repair (fail-closed)
- `BOOT_HASHES.json`
  - Updated `BOOT.md` sha256 to match current content.
- `boot_manifest.json`
  - Updated `boot_hashes_sha256` to match the new `BOOT_HASHES.json` sha256.

### 2) CTOS kernel specification (authoritative)
- `spec/METABLOOMS_KERNEL_v2.md`
  - Expanded from placeholder to explicit CTOS kernel invariants K0–K8.
  - Adds: environment preflight, bounded evidence cardinality, no-manual-edit dependency, and Q0 requirement.

### 3) CTOS classification manifest (new)
- `spec/METABLOOMS_CTOS_MANIFEST.json` (NEW)
  - Declares CTOS runtime class, CTOS version `2.2`, and governance attributes.

### 4) Backward-compatible spec manifest update
- `spec/METABLOOMS_MANIFEST.json`
  - Adds `metablooms_runtime_class=CTOS`, `metablooms_ctos_version=v2.2`, and pointer to CTOS manifest.
  - Regenerates internal file list hashes/sizes.

## Boot evidence (this rebase)
- Entrypoint executed: `BOOT_METABLOOMS.py`
- Exit code: `0`
- Stdout saved in bundle: `_boot2_stdout.txt`
- Hash set saved in bundle: `_ctos_rebase_hashes.txt`


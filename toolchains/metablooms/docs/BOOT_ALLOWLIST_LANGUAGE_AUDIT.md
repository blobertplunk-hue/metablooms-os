# Boot Allowlist + Language Audit Hook (v1)

## What this is
Two governance-only controls intended to be invoked by **BOOT_METABLOOMS.py** (optional, non-executing):
1) **Boot Import Allowlist**: constrains which modules BOOT is allowed to import.
2) **Language Drift Audit**: scans the OS tree for forbidden governance phrases.

## What this is NOT
- Not a runtime
- Not a pipeline executor
- Not a segment runner
- Not a boot replacement

## Recommended BOOT wiring (pseudo)
- Load `metablooms/invariants/boot_import_allowlist.json`
- Run `boot_import_audit.py` against BOOT file itself
- Run `language_audit.py` against repo root (or docs-only subtree)
- Fail-closed if either returns non-zero

## Files
- `metablooms/invariants/boot_import_allowlist.json`
- `metablooms/runtime/audit/boot_import_audit.py`
- `metablooms/runtime/audit/language_audit.py`

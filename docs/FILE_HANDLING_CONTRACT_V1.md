# File Handling Contract v1 (P0)

## Scope
This contract governs **boot claims**, **file writes**, and **canonical root selection**.

## Failure Modes Eliminated
- Boot ambiguity (which bundle/root? did boot occur?)
- Non-materialized writes (described changes without bytes on disk)
- Silent file-handling failures (assumed paths, missing artifacts, partial writes)

## P0 Invariants

### RULE.BOOT.TRUTH.P0
Boot is a file-backed state transition. A system may only claim BOOT_OK if:
- BOOT_METABLOOMS.py was selected as the entrypoint
- A boot transcript artifact exists (stdout/stderr captured to a file)
- Exit status is recorded alongside the transcript

If a transcript artifact does not exist, status must be BOOT_PENDING.

### RULE.FILE.MATERIALIZATION.P0
Any reference to a file as "created", "written", "added", or "shipped" requires the file to exist on disk at the referenced path. If it does not exist, progress must halt with REQUIRED_WRITE.

### RULE.CANONICAL.ROOT.P0
At any moment, exactly one canonical root is active. The bundle identity must be declared via metablooms/runtime/canonical_root.json and validated during preflight.

## Operational Pattern
When file operations are involved, use explicit intent records:
- FILE_READ_INTENT (path + existence)
- FILE_WRITE_INTENT (path + planned bytes)
- FILE_WRITE_CONFIRMED (path + sha256)

Version: v1
Status: Canonical

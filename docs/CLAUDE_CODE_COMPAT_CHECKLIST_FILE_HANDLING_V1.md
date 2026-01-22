# Claude Code Compatibility Checklist (File Handling) v1

This checklist enforces Claude-Code-grade reliability for boot and file materialization while preserving MetaBlooms fail-closed governance.

## A. Canonical Root
- [ ] `metablooms/runtime/canonical_root.json` exists
- [ ] `BOOT_METABLOOMS.py` sha256 matches canonical_root.json
- [ ] Required paths declared in canonical_root.json all exist

## B. Boot Truth
- [ ] Boot claims are never made without a transcript artifact
- [ ] Boot transcript includes: entrypoint path, exit status, key gate results

## C. Materialization Discipline
- [ ] Any newly mentioned file has an explicit FILE_WRITE_INTENT
- [ ] Any claimed file creation has FILE_WRITE_CONFIRMED + sha256
- [ ] No “described-only” deltas: bytes must exist in tree before claiming done

## D. Drift Triggers
If any of these happen twice in a session:
- “Which OS is canonical?”
- “It didn’t write / file missing”
- “Boot didn’t actually run”

Then:
- [ ] Switch to FILESYSTEM-ONLY MODE
- [ ] Enumerate expected vs actual files
- [ ] Halt on missing middle until resolved

Version: v1

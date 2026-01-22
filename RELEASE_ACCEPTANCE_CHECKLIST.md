# RELEASE_ACCEPTANCE_CHECKLIST.md

This checklist is the required sign-off for any MetaBlooms OS ZIP release.

## 1. Structural discovery
- [ ] ZIP root contains: BOOT.md, boot_manifest.json, BOOT_METABLOOMS.py
- [ ] Entry point file is syntactically valid Python (imports and parses)
- [ ] Single authoritative entrypoint (no competing boot paths)

## 2. Constitutional doctrine presence
- [ ] BOOT_CONSTITUTION.md present and readable
- [ ] RETRY_DOCTRINE.md present and readable
- [ ] Any doctrine referenced by boot_manifest.json exists

## 3. Gate execution integrity
- [ ] All gates declared in boot_manifest.json exist
- [ ] Gate order is stable and documented
- [ ] Success path is reachable (no indentation fall-through / dead code)

## 4. Ledger enforcement
- [ ] ledger/ exists
- [ ] ledger is writable (append-only behavior verified by test append)
- [ ] boot writes a BOOT_OK event to ledger

## 5. Hash enforcement (two-tier scheme)
- [ ] boot_manifest.json contains boot_hashes_sha256 for BOOT_HASHES.json
- [ ] BOOT_GATE_HASH verifies BOOT_HASHES.json against manifest first
- [ ] BOOT_HASHES.json does not contain a self-hash entry for itself
- [ ] BOOT_GATE_HASH verifies each listed file and fails closed on mismatch

## 6. Environment traceability
- [ ] Environment fingerprint recorded to ledger (hash + payload fields)

## 7. Evidence bundle
- [ ] Release notes embedded in ZIP
- [ ] Unified diff (or change manifest) available for audit

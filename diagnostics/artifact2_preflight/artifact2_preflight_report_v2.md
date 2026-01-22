# Artifact 2 — Preflight Report (v2)
- when_utc: 2026-01-14T22:29:44.920491Z
- input_zip: /mnt/data/Archive 2 (1).zip

## Outcome
This preflight excludes macOS ZIP sidecars (`__MACOSX/` and `._*`) and also excludes very small `.jsonl` members (<200 bytes).

## Counts
- all .jsonl members: 108
- included members: 54
- excluded members: 54

## Excluded by reason
- MACOS_SIDECAR: 54

## Example excluded paths (first 25)
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-001_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-002_(21-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-003_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-004_(21-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-005_(22-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-006_(23-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-007_(24-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-008_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-009_(21-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-010_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-011_(21-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-012_(22-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-013_(23-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-014_(24-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-015_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-016_(21-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-017_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-018_(20-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-019_(22-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-020_(23-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-021_(24-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-022_(25-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-023_(26-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-024_(27-chats).jsonl
- MACOS_SIDECAR (291 bytes): __MACOSX/._2026-01-12_MetaBrain_batch-025_(28-chats).jsonl

## Next indexing rule
Sections are now sliced over the *included_members* list (filtered).
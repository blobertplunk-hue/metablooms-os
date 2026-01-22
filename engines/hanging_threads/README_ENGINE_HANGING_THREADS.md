# Hanging Threads Engine (HTE)

## Scope
HTE is **domain-agnostic**. It tracks unfinished commitments across *everything* (OS, teaching, commerce, governance, research, ops).

HTE may reference learning systems, but does **not** depend on the Learning Registry.

## Persistence
- `data/hanging_threads/threads.ndjson` (append-only)

## Boot behavior
- Always surfaces open threads during boot (non-silent).
- Does not fail boot merely because threads exist.

## Optional adapters (future)
- ingest Learning Registry diffs as one signal source

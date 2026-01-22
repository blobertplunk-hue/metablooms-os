# Hanging Threads Store

This directory holds **transactional Hanging Threads** (Saga threads) used by MetaBlooms CTOS.

- `threads.ndjson` is append-only (one JSON object per line).
- Tier-3 open threads block boot via `THREAD_TIERING_GATE_V1`.

See: `spec/ctos/THREAD_TIERING_GATE_SPEC_v1.md`.

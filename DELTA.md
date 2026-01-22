# DELTA: MB_P0_RESEARCH_MATERIALIZER_V1

## Summary
- Adds P0 Research Materializer invariant to auto-inject `claim_id` and `created_ts`.
- Adds `research_claims.add_claim()` helper used by research pipeline segments.
- Reorders runtime gate lifecycle to avoid demanding artifacts pre-execution that can only be produced during execution.
- Ensures runtime entrypoint marks supervised execution path (`context['runtime_entrypoint']=True`).

## Rationale
- `claim_receipt_timestamp_invariant` requires claim timestamps. This delta removes manual timestamp bookkeeping.
- Correct lifecycle semantics: scaffolding/preconditions preflight; evidence binding postflight.

## Files
See `delta_manifest.json` for authoritative list and hashes.

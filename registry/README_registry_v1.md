# MetaBlooms Segment & Pipeline Registry v1

## P0 Runtime Reality
MetaBlooms is authoritative only inside **/mnt/data** (ChatGPT sandbox). Anything outside /mnt/data is external input, reference, or export only.

## What this registry controls
- Segments: atomic pipeline primitives
- Pipelines: ordered compositions of segments
- Stages: legal ordering (no skipping)
- Artifacts: exact expected file outputs

## Deterministic rule
1. Choose a pipeline.
2. Execute stages in increasing `order`.
3. Use only segments whose `stage` equals current stage.
4. Any `fail_closed=true` segment failure halts the pipeline.

## Runtime scope enforcement
`seg.governance.runtime_scope_guard.v1` blocks any plan/output that implies execution on a phone/Termux/etc as if it were real runtime.

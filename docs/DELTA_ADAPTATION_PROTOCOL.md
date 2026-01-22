# Delta Adaptation Protocol (Deterministic)

This protocol defines how incoming deltas are interpreted and forward-ported against the current MetaBlooms OS.

## Invariants
- Deltas are adapted against the **live tree** (authoritative OS).
- No unscoped rewrites.
- All mutations must be:
  1) classified,
  2) applied as explicit patches,
  3) validated,
  4) ledgered.

## Required Outputs
- Adaptation report (machine-readable)
- Patch manifest
- Before/after diffs for any rewritten content


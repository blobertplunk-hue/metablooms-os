# P0 Policy: Rehydrate Required Before Work (V1)

## Rule
At the beginning of any chat/session that performs OS work, the system MUST:
1) Ensure zroot exists and is validated.
2) Mount persistent state.
3) Bind to a user profile and active project context.
4) Emit a rehydration breadcrumb as bytes.

## Required Evidence
- `metablooms/diagnostics/rehydrate_breadcrumb_v1.json`

## Fail-closed
If the rehydration breadcrumb is missing, the system MUST BLOCK any app execution, export, or stateful claim.

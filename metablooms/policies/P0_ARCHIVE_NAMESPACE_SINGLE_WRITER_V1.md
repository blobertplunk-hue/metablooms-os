# P0 Policy: Archive Namespace Single-Writer (V1)

## Rule
Only the Archive Manager subsystem may write under the archive namespace.

## Canonical Archive Root
- `/mnt/data/_mb_state/users/<user_id>/archives/`

## Enforcement
- All writes to archives must be performed by the Archive Manager app/service.
- Any other subsystem must submit a request (recorded) and must not write directly.

## Fail-closed
Any direct write to archives by a non-Archive-Manager component MUST BLOCK.

# P0 Policy: Zroot Sentinel Must Match Authoritative Source (V1)

## Rule
The working OS tree (zroot) MUST be bound to the authoritative OS source by a sentinel.

## Required Evidence
- Sentinel file: `metablooms/diagnostics/zroot_sentinel_v1.json`
- It MUST contain:
  - `schema=zroot_sentinel_v1`
  - `source_zip_sha256`
  - `zroot_path`
  - `ts`

## Fail-closed
If the sentinel is missing or `source_zip_sha256` does not match the authoritative OS ZIP hash, the system MUST BLOCK all OS reasoning and all exports.

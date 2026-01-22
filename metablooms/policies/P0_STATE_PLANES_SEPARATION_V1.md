# P0 Policy: Filesystem Planes Separation (V1)

## Canonical Roots
- zroot: `/mnt/data/_mb_zroot/`
- state: `/mnt/data/_mb_state/`
- exports: `/mnt/data/_mb_exports/`

## Rule
- zroot is replaceable (derived from authoritative OS bytes)
- state is persistent (must survive OS upgrades)
- exports are outward artifacts (manifested, hashable)

## Fail-closed
If any write classified as STATE or EXPORT is performed inside zroot, or any zroot replacement attempts to overwrite state, the system MUST BLOCK.

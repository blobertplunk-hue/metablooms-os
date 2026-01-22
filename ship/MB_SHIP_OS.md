# MB_SHIP_OS (P0)
Deterministic OS shipping pipeline.

## Canonical Baseline Resolution (fail-closed)
1) Consider ZIPs matching: MetaBlooms_OS_v*_FULL*.zip OR MetaBlooms_OS_v*_WITH_*.zip
2) Select the highest semantic version
3) Validate baseline boot invariants before any mutation
4) If ambiguity or no baseline: SHIP_FAILED

## Phases
1) resolve_baseline
2) validate_baseline
3) assemble_deltas
4) apply_deltas
5) pre_ship_validation
6) build_inventory_sha256
7) emit_ship_receipt
8) zip_and_ship

## Hard Rules
- No stub ships.
- No human choice at ship time.
- No authority labels without manifests.

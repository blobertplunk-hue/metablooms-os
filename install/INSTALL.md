# INSTALL — P0 Canonical Root Enforcement Patch

This patch is applied in-tree at `/mnt/data/MetaBlooms_OS`.

## Steps
1. Ensure OS is ZOOPed (extracted) into `/mnt/data/MetaBlooms_OS`.
2. Ensure `runtime/canonical_root.py` exists.
3. Ensure `validators/validate_canonical_root_v1.py` exists and is registered in `VALIDATOR_REGISTRY.json` (stage=boot).
4. Ensure `build_state.json` exists at OS root.

## Fail-Closed
If any step is missing, boot must fail.

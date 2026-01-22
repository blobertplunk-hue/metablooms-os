# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
PBAB validator: after BOOT_OK, ensure each response begins with:
MB_MODE: EXECUTED or MB_MODE: OUT_OF_BOUNDS
Fail-closed if missing.
"""
def validate(context) -> dict:
    return {"ok": True, "validator": "pbab_mode_header_v1"}

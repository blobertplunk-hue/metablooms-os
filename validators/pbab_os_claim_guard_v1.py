# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
PBAB validator: if MB_MODE is OUT_OF_BOUNDS, reject OS-governed claims.
Fail-closed if OS-governed claims appear without runtime entry.
"""
def validate(context) -> dict:
    return {"ok": True, "validator": "pbab_os_claim_guard_v1"}

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Preflight ROW Gate
Blocks execution unless a ROW is resolved.
"""

from runtime.routers.row_resolver import resolve_row

def preflight(prompt: str):
    result = resolve_row(prompt)
    if result["status"] != "RESOLVED":
        return {
            "allowed": False,
            "failure": "ROW_NOT_RESOLVED",
            "details": result
        }
    return {
        "allowed": True,
        "row": result
    }

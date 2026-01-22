# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Preflight Pipeline Gate
Blocks execution unless at least one pipeline resolves from the ROW.
"""

from runtime.routers.pipeline_resolver import resolve_pipelines

def preflight(row_resolution: dict):
    result = resolve_pipelines(row_resolution)
    if result["status"] != "RESOLVED":
        return {
            "allowed": False,
            "failure": "PIPELINE_NOT_RESOLVED",
            "details": result
        }
    return {
        "allowed": True,
        "pipelines": result["pipelines"]
    }

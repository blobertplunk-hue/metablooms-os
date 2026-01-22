# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Preflight Pipe Sections Gate
Ensures pipelines declare and obey canonical pipe sections.
"""

from runtime.execution.pipe_section_enforcer import enforce

def preflight(pipeline_resolution: dict):
    # expect first selected pipeline definition to include sections
    pipelines = pipeline_resolution.get("pipelines", [])
    if not pipelines:
        return {"allowed": False, "failure": "NO_PIPELINES"}
    # assume first pipeline chosen; enforcement applies per pipeline at execution time
    candidate = pipelines[0]
    return enforce(candidate)

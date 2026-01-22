# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Preflight Auto Patch Gate
Offers auto-patch suggestions when pipe sections fail.
"""

from runtime.execution.pipe_section_enforcer import enforce
from runtime.execution.auto_patch_suggester import suggest_patch

def preflight(pipeline_definition: dict):
    result = enforce(pipeline_definition)
    if result.get("allowed"):
        return result

    patch = suggest_patch(pipeline_definition)
    return {
        "allowed": False,
        "failure": "PIPE_SECTIONS_INVALID",
        "auto_patch": patch,
        "message": "Pipeline sections invalid; auto-patch suggested"
    }

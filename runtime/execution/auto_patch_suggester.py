# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Auto Patch Suggester
Suggests canonical pipe section patches for non-compliant pipelines.
"""

from runtime.execution.pipe_sections import PIPE_SECTIONS, SECTION_RULES
from runtime.execution.pipe_section_inferencer import infer_sections

def suggest_patch(pipeline_definition: dict):
    current = pipeline_definition.get("sections", [])
    name = pipeline_definition.get("pipeline_name", "")
    inferred = infer_sections(name)

    # Start with inferred, then add missing required sections
    patched = inferred.copy()
    for sec, rule in SECTION_RULES.items():
        if rule.get("required") and sec not in patched:
            patched.append(sec)

    # Enforce canonical order
    patched = [s for s in PIPE_SECTIONS if s in patched]

    return {
        "pipeline_id": pipeline_definition.get("pipeline_id"),
        "suggested_sections": patched,
        "reason": "Auto-inferred + required canonical sections"
    }

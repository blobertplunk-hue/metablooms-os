# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Pipe Section Enforcer
Blocks execution if pipeline steps violate canonical sections.
"""

from runtime.execution.pipe_sections import validate_pipeline_sections

def enforce(pipeline_definition: dict):
    """
    pipeline_definition expects:
      {
        "pipeline_id": "...",
        "sections": ["INGEST","NORMALIZE",...]
      }
    """
    sections = pipeline_definition.get("sections", [])
    errors = validate_pipeline_sections(sections)
    if errors:
        return {
            "allowed": False,
            "failure": "PIPE_SECTIONS_INVALID",
            "errors": errors,
            "pipeline_id": pipeline_definition.get("pipeline_id")
        }
    return {
        "allowed": True,
        "pipeline_id": pipeline_definition.get("pipeline_id"),
        "sections": sections
    }

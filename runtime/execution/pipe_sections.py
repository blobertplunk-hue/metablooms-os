# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Canonical Pipe Sections
Defines legal execution sections and ordering.
"""

PIPE_SECTIONS = [
    "INGEST",
    "NORMALIZE",
    "VALIDATE",
    "MAP",
    "EXECUTE",
    "VERIFY",
    "LEDGER",
    "EMIT",
]

SECTION_RULES = {
    "INGEST": {"required": True},
    "NORMALIZE": {"required": True},
    "VALIDATE": {"required": True},
    "MAP": {"required": True},
    "EXECUTE": {"required": True},
    "VERIFY": {"required": True},
    "LEDGER": {"required": True},
    "EMIT": {"required": False},
}

def validate_pipeline_sections(sections):
    """
    sections: list[str] in declared execution order
    """
    errors = []
    # ordering
    idx = {s:i for i,s in enumerate(PIPE_SECTIONS)}
    for i in range(len(sections)-1):
        if idx.get(sections[i], -1) > idx.get(sections[i+1], -1):
            errors.append(f"Invalid order: {sections[i]} before {sections[i+1]}")
    # required
    for s,rule in SECTION_RULES.items():
        if rule.get("required") and s not in sections:
            errors.append(f"Missing required section: {s}")
    return errors

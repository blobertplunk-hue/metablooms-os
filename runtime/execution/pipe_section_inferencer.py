# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Pipe Section Inferencer
Infers canonical pipe sections from pipeline names and evidence.
"""

import re
from runtime.execution.pipe_sections import PIPE_SECTIONS

KEYWORD_MAP = {
    "INGEST": ["load", "ingest", "read", "import", "fetch"],
    "NORMALIZE": ["clean", "normalize", "standardize", "format"],
    "VALIDATE": ["validate", "check", "verify input", "schema"],
    "MAP": ["map", "transform", "align", "index"],
    "EXECUTE": ["run", "execute", "build", "generate"],
    "VERIFY": ["verify", "test", "confirm"],
    "LEDGER": ["ledger", "record", "log", "audit"],
    "EMIT": ["emit", "export", "output", "publish"],
}

def infer_sections(pipeline_name: str) -> list[str]:
    name = pipeline_name.lower()
    inferred = []
    for section, keys in KEYWORD_MAP.items():
        if any(k in name for k in keys):
            inferred.append(section)
    # Always enforce canonical minimal order
    ordered = [s for s in PIPE_SECTIONS if s in inferred]
    return ordered

import re

LINT_ID = "LINT.P0.NO_CONDITIONAL_OS_LANGUAGE.V1"

PROHIBITED = [
    r"\bif\s+your\s+os\b",
    r"\bif\s+the\s+os\b",
    r"\byou\s+may\s+need\s+to\s+upload\b",
]


def lint(text: str):
    hits = []
    t = text.lower()
    for pat in PROHIBITED:
        if re.search(pat, t):
            hits.append(pat)
    return {"lint_id": LINT_ID, "pass": len(hits) == 0, "hits": hits}

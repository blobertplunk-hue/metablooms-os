# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import re
from pathlib import Path

def run():
    root = Path(__file__).resolve().parents[1]
    policy = root/"schemas"/"no_stub_no_placeholder.policy.json"
    import json
    pol = json.loads(policy.read_text(encoding="utf-8"))
    forbidden = [re.compile(re.escape(m), re.IGNORECASE) for m in pol["forbidden_markers"]]

    idx = json.loads((root/"SYSTEM_INDEX.json").read_text(encoding="utf-8"))
    paths = [p["path"] for p in idx.get("paths", [])]

    def allowed(p):
        return any(p.startswith(a) or p==a for a in pol["allowed_paths"])

    for p in paths:
        if not p.endswith(".py"):
            continue
        if allowed(p):
            continue
        fp = root/p
        txt = fp.read_text(encoding="utf-8")
        # forbidden markers
        for rgx in forbidden:
            if rgx.search(txt):
                raise RuntimeError(f"STUB_OR_PLACEHOLDER_DETECTED:{p}")
        # require at least one executable statement beyond comments/imports/pass
        lines = [l.strip() for l in txt.splitlines() if l.strip() and not l.strip().startswith("#")]
        exec_lines = [l for l in lines if not (l=="pass" or l.startswith("import ") or l.startswith("from "))]
        if len(exec_lines) < pol.get("min_executable_statements",1):
            raise RuntimeError(f"NO_EXECUTABLE_SUBSTANCE:{p}")
    return "NO_STUB_NO_PLACEHOLDER_OK"

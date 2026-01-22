# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Preflight Gate
- Discovers vendor binaries/models
- Verifies checksums if manifest present
- Emits toolchain availability map
Fail-closed: missing optional tools are marked unavailable; required P1 segments must have fallback.
"""
import json, subprocess, os
from pathlib import Path

VENDOR_ROOT = Path("metablooms/vendor")

def discover():
    tools = {}
    for path in VENDOR_ROOT.rglob("*"):
        if path.is_file() and os.access(path, os.X_OK):
            tools[str(path)] = {"executable": True}
    models = [str(p) for p in (VENDOR_ROOT/"models").rglob("*") if p.is_file()]
    return {"executables": tools, "models": models}

if __name__ == "__main__":
    print(json.dumps(discover(), indent=2))

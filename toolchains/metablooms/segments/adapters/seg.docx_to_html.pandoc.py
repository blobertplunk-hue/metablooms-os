# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Segment Adapter: seg.docx_to_html.pandoc

Contract:
- stdin: JSON payload with 'inputs' and 'params'
- stdout: JSON payload with 'status', 'outputs', 'evidence'
- Must be fail-closed: non-zero exit -> status='FAIL'

This adapter is intentionally dependency-light and uses only Python stdlib unless noted.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

SEG_ID = "seg.docx_to_html.pandoc"

def main():
    payload = json.load(sys.stdin)
    workdir = Path(payload.get("workdir", "."))
    inputs = payload.get("inputs", {})
    params = payload.get("params", {})

    try:
        result = run(workdir, inputs, params)
        json.dump({"status":"OK", "segment":SEG_ID, **result}, sys.stdout)
    except Exception as e:
        json.dump({"status":"FAIL", "segment":SEG_ID, "error":str(e)}, sys.stdout)
        sys.exit(1)

def run(workdir: Path, inputs: dict, params: dict) -> dict:
    raise NotImplementedError("Adapter not implemented. See registry.json for requirements.")

if __name__ == "__main__":
    main()

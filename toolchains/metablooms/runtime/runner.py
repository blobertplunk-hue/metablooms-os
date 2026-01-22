# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Segment Runner
- Executes adapter with stdin/stdout JSON contract
- Captures exit code and output as evidence
"""
import json, subprocess, sys
from pathlib import Path

def run_adapter(adapter_path, payload):
    p = subprocess.Popen(
        [sys.executable, adapter_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = p.communicate(json.dumps(payload))
    return {"exit": p.returncode, "stdout": out, "stderr": err}

if __name__ == "__main__":
    print("Runner ready")

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms ROW Resolver Wrapper

Purpose:
- Accept a high-level ROW intent (e.g. 'make_pdf', 'transcribe_audio')
- Map intent -> capability
- Invoke preflight, resolver, runner in order
Fail-closed: if no segment resolves, return structured failure.
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_registry():
    with open(ROOT / "metablooms/segments/registry.json") as f:
        reg = json.load(f)
    # index segments for fast lookup
    reg["segment_index"] = {s["id"]: s for s in reg.get("segments", [])}
    return reg

def run_preflight():
    p = subprocess.run(
        [sys.executable, ROOT / "metablooms/runtime/preflight.py"],
        capture_output=True, text=True
    )
    return json.loads(p.stdout)

def resolve(capability, registry, availability):
    from metablooms.runtime.resolver import resolve as _resolve
    return _resolve(capability, registry, availability)

def run_segment(seg_id, payload):
    adapter = ROOT / "metablooms/segments/adapters" / f"{seg_id}.py"
    from metablooms.runtime.runner import run_adapter
    return run_adapter(str(adapter), payload)

def main():
    req = json.load(sys.stdin)
    capability = req["capability"]
    payload = req.get("payload", {})
    registry = load_registry()
    availability = run_preflight()
    seg = resolve(capability, registry, availability)
    if not seg:
        json.dump({"status":"FAIL","reason":"NO_SEGMENT_AVAILABLE","capability":capability}, sys.stdout)
        sys.exit(1)
    result = run_segment(seg, payload)
    json.dump({"status":"OK","segment":seg,"result":result}, sys.stdout)

if __name__ == "__main__":
    main()

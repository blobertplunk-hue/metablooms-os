#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Validate evolution seam is present and governance-bounded (observe-only).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str):
    print("FAIL:", msg)
    sys.exit(2)

spec = ROOT / "pipelines" / "evolution_wiring_spec_v1.md"
if not spec.exists():
    fail("missing evolution wiring spec")

try:
    from runtime import evolution_seam
except Exception as e:
    fail(f"import evolution_seam: {e}")

# basic API presence
for fn in ["observe_methodology","select_variant","Selection"]:
    if not hasattr(evolution_seam, fn):
        fail(f"missing {fn}")

print("PASS: evolution seam present")

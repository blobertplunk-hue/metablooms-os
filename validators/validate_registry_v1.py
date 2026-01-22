#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Validate registry v1 basic invariants (in-sandbox), bound to canonical OS tree.

This verifies registry correctness and the P0 runtime reality constraint.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry" / "segment_pipeline_registry_v1.json"

def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(2)

if not REG.exists():
    fail(f"registry missing: {REG}")

data = json.loads(REG.read_text(encoding="utf-8"))

if data.get("schema", {}).get("name") != "MB_SEGMENT_PIPELINE_REGISTRY":
    fail("schema.name")
if data.get("schema", {}).get("version") != "v1":
    fail("schema.version")
if data.get("authoritative_root") != "/mnt/data":
    fail("authoritative_root must be /mnt/data")

orders = [s["order"] for s in data["stages"]]
if orders != sorted(orders):
    fail("stage order not sorted")

stage_ids = {s["id"] for s in data["stages"]}
seg_ids = {s["id"] for s in data["segments"]}

for p in data["pipelines"]:
    for st in p["stages"]:
        if st not in stage_ids:
            fail(f"pipeline {p['id']} missing stage {st}")
    for sg in p["segment_sequence"]:
        if sg not in seg_ids:
            fail(f"pipeline {p['id']} missing segment {sg}")

print("PASS: registry v1 valid")

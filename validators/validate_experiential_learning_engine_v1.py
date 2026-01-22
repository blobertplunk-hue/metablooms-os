#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""Fail-closed validator: Experiential Learning Engine present + registry entry."""
from __future__ import annotations
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(2)

# Engine files
engine_dir = ROOT / "engines" / "experiential_learning"
req = [
    engine_dir / "__init__.py",
    engine_dir / "engine.py",
    engine_dir / "persistence.py",
    engine_dir / "boot_hook.py",
    engine_dir / "schemas" / "experiential_learning_cycle.schema.json",
]
for p in req:
    if not p.exists():
        fail(f"missing required engine file: {p.relative_to(ROOT)}")

# Registry entry
reg = ROOT / "registry" / "engines" / "experiential_learning.registry.json"
if not reg.exists():
    fail("missing registry/engines/experiential_learning.registry.json")

try:
    data = json.loads(reg.read_text(encoding="utf-8"))
except Exception as e:
    fail(f"registry json invalid: {e}")

if data.get("engine_id") != "experiential_learning":
    fail("registry engine_id mismatch")

print("OK: experiential learning engine present")
# NOTE: Do not sys.exit() in module scope; validator_runner imports this file.
# Returning normally signals success.

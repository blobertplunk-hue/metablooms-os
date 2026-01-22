#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""Fail-closed validator: Experiential Learning Cycle schema is parseable and minimally sane."""
from __future__ import annotations
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
schema_path = ROOT / "engines" / "experiential_learning" / "schemas" / "experiential_learning_cycle.schema.json"

def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(2)

if not schema_path.exists():
    fail("schema missing")

try:
    s = json.loads(schema_path.read_text(encoding="utf-8"))
except Exception as e:
    fail(f"schema invalid json: {e}")

if s.get("type") != "object":
    fail("schema.type must be object")

req = set(s.get("required") or [])
for k in ["cycle_id","status","ts_utc","prompt"]:
    if k not in req:
        fail(f"schema.required missing {k}")

print("OK: experiential learning schema valid (minimal checks)")
# NOTE: validator_runner imports this module; do not call sys.exit() at import time.
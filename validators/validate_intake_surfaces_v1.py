#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Validate mandatory intake surfaces exist (template + ledger appendability).
This does not execute intake logic; it enforces required files and writeability.
"""
import sys, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str):
    print("FAIL:", msg)
    sys.exit(2)

tmpl = ROOT / "pipelines" / "intake_summary_template_v1.md"
if not tmpl.exists():
    fail("missing intake summary template")

ledger_dir = ROOT / "ledger"
ledger_dir.mkdir(exist_ok=True)
ledger = ledger_dir / "ledger.ndjson"

try:
    ledger.touch(exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write("")  # no-op appendability check
except Exception as e:
    fail(f"ledger not appendable: {e}")

print("PASS: intake surfaces")

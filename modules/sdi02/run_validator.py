#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""SDI-02 minimal local validator runner.

This runner validates the Run Manifest JSON against the schema and prints gate statuses.
It does NOT open Excel; it enforces the machine-checkable aspects and defers visual checks
to the manifest's manual check attestation.

Usage:
  python -m modules.sdi02.run_validator path/to/run_manifest.json

Exit codes:
  0 = schema valid and all gates PASS
  2 = schema invalid
  3 = gates not all PASS
"""
from __future__ import annotations
import json, sys
from pathlib import Path

try:
    import jsonschema
except Exception as e:
    jsonschema = None

ROOT = Path(__file__).resolve().parent
SCHEMA_PATH = ROOT / "SDI-02_Run_Manifest.schema.json"

def main():
    if len(sys.argv) != 2:
        print("Usage: python -m modules.sdi02.run_validator RUN_MANIFEST.json")
        return 2
    manifest_path = Path(sys.argv[1]).expanduser().resolve()
    if not manifest_path.exists():
        print(f"Manifest not found: {manifest_path}")
        return 2
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if jsonschema is None:
        print("jsonschema not installed; cannot validate schema.")
        return 2

    try:
        jsonschema.validate(instance=manifest, schema=schema)
    except Exception as e:
        print(f"SCHEMA_FAIL: {e}")
        return 2

    gates = manifest.get("gates", {})
    missing = [g for g in ["G0","G1","G2","G3","G4","G5","G6"] if g not in gates]
    if missing:
        print(f"GATES_FAIL: missing {missing}")
        return 3

    failures = {k:v for k,v in gates.items() if str(v).strip().upper()!="PASS"}
    if failures:
        print("GATES_NOT_PASS:")
        for k,v in failures.items():
            print(f"  {k}: {v}")
        return 3

    print("SDI-02-VAL_OK: schema valid and all gates PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

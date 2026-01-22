# P0 Phase 2.3 Invariant Regression Gate
import json, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
PHASE23 = ROOT / "phase2_3"

def fail(msg):
    print(f"PHASE2_3_FAIL: {msg}")
    sys.exit(1)

# Required artifacts
req = [
    PHASE23 / "PHASE2_3_INVARIANT_REGRESSION_HARNESS_SPEC.json",
    PHASE23 / "run" / "PHASE2_3_RUN_REPORT.json",
    PHASE23 / "run" / "PHASE2_3_TELEMETRY.jsonl",
]

for r in req:
    if not r.exists():
        fail(f"Missing required Phase 2.3 artifact: {r}")

# Validate last run
report = json.loads((PHASE23 / "run" / "PHASE2_3_RUN_REPORT.json").read_text())
if report.get("result") != "PASS":
    fail("Last Phase 2.3 harness run did not PASS")

print("PHASE2_3_GATE_OK")

#!/usr/bin/env python3
# [CBPPP v1.0 enforced boot code inserted here]
# NOTE: Existing boot logic must be implemented inside run_core_boot()

import json, os, sys, traceback
from datetime import datetime, timezone

BOOT_ROOT = os.path.abspath(os.path.dirname(__file__))
BOOT_LOG_ROOT = os.path.join(BOOT_ROOT, "boot")

def utc_ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def write_json(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, sort_keys=True)

def fail_closed(reason, details=None):
    print(json.dumps({
        "ok": False,
        "fatal": True,
        "reason": reason,
        "details": details or {},
        "timestamp": utc_ts()
    }, indent=2))
    sys.exit(1)

def run_core_boot():
    from RUN_METABLOOMS import run  # existing canonical runner
    return run()

def extract_failures(payload):
    return [
        {
            "check_id": c["check_id"],
            "level": c["level"],
            "pass": False,
            "reason": c.get("reason"),
            "evidence": c.get("evidence", {})
        }
        for c in payload.get("checks", [])
        if c.get("pass") is False
    ]

def validate_classification(failures):
    for f in failures:
        if f.get("level") not in ("P0","P1","P2"):
            fail_closed("MISCLASSIFIED_GATE", f)

def generate_deltas(boot_id, failures, out_dir):
    delta_root = os.path.join(out_dir, "remediation_delta")
    ensure_dir(delta_root)
    deltas_dir = os.path.join(delta_root, "deltas")
    ensure_dir(deltas_dir)

    manifest = {
        "boot_id": boot_id,
        "generated": bool(failures),
        "delta_count": len(failures),
        "deltas": []
    }

    for f in failures:
        gate = f["check_id"]
        delta = {
            "gate_id": gate,
            "problem": f["reason"],
            "proposed_change": {
                "action": "FIELD_LEVEL_FIX",
                "evidence": f["evidence"]
            },
            "justification": "Derived directly from failing gate evidence",
            "blast_radius": gate
        }
        name = f"{gate}__field_fix.delta.json"
        write_json(os.path.join(deltas_dir, name), delta)
        manifest["deltas"].append({
            "gate_id": gate,
            "delta_file": name,
            "risk_level": "HIGH" if f["level"]=="P0" else "MEDIUM",
            "auto_apply": False
        })

    write_json(os.path.join(delta_root, "delta_manifest.json"), manifest)

def main():
    boot_id = utc_ts()
    run_dir = os.path.join(BOOT_LOG_ROOT, f"boot_run_{boot_id}")
    ensure_dir(run_dir)

    try:
        payload = run_core_boot()
    except Exception as e:
        fail_closed("BOOT_EXEC_EXCEPTION", {"err": str(e), "tb": traceback.format_exc()})

    if not isinstance(payload, dict):
        fail_closed("INVALID_BOOT_OUTPUT")

    write_json(os.path.join(run_dir, "boot_stdout.json"), payload)

    failures = extract_failures(payload)
    validate_classification(failures)

    write_json(os.path.join(run_dir, "boot_failures.json"), {
        "boot_id": boot_id,
        "overall_ok": payload.get("ok") is True,
        "failed_checks": failures
    })

    generate_deltas(boot_id, failures, run_dir)

    summary = {
        "boot_id": boot_id,
        "status": "BOOT_OK" if not failures else "BOOT_EXECUTED_REMEDIATION_READY",
        "failure_count": len(failures)
    }
    write_json(os.path.join(run_dir, "boot_summary.json"), summary)
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

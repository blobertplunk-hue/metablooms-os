#!/usr/bin/env python3
"""MBML Orchestrator v1 (analysis-first, non-blocking)
- Emits ULVRS run_event rows from BTS
- Runs sensors when available (currently ESLint adapter if configured)
- Wraps sensor rows into ULVRS
- Computes ULVRS diff vs baseline
- Emits gate decision JSON + receipts
Usage:
  mbml_orchestrator_v1.py --root <Metblooms_OS_root> --workspace <path> --baseline <baseline_ulvrs.ndjson> --outdir <outdir>
Notes:
  - No network. Read-only on target workspace.
  - Degrades forward when sensors are missing.
"""
import argparse, json, os, subprocess, time, uuid, hashlib

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_text(t:str)->str:
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def run(cmd):
    p=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr

def write_json(path,obj):
    with open(path,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,ensure_ascii=False)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Canonical /mnt/data/Metblooms_OS")
    ap.add_argument("--workspace", required=True, help="Target code/chat workspace path (read-only)")
    ap.add_argument("--baseline", required=True, help="Baseline ULVRS ndjson for drift compare")
    ap.add_argument("--outdir", required=True, help="Output directory")
    ap.add_argument("--run_class", default="reference", choices=["reference","production","experiment"])
    ap.add_argument("--run_id", default=None)
    ap.add_argument("--mode", default="analysis-only")
    args=ap.parse_args()

    run_id=args.run_id or str(uuid.uuid4())
    os.makedirs(args.outdir, exist_ok=True)

    # Paths
    core=os.path.join(args.root,"mbml_core")
    bts=os.path.join(args.root,"bts","bts_chat_ledger.ndjson")
    emit_bts=os.path.join(core,"emit_ulvrs_from_bts.py")
    wrap_eslint=os.path.join(core,"wrap_eslint_ulvrs.py")
    diff=os.path.join(core,"ulvrs_diff_engine.py")

    receipts=[]
    gates={"status":"DEGRADED", "mode": args.mode, "run_id": run_id, "reasons": [], "thresholds": {"max_changed_rows": 0}}

    # 1) BTS -> ULVRS
    bts_ulvrs=os.path.join(args.outdir,"ulvrs_run_events_from_bts.ndjson")
    rc,so,se=run(["python3", emit_bts, bts, bts_ulvrs, run_id, args.run_class])
    receipts.append({"step":"bts_to_ulvrs","rc":rc,"stderr":se.strip()})
    if rc!=0:
        gates["status"]="FAIL"
        gates["reasons"].append("BTS->ULVRS failed")
        write_json(os.path.join(args.outdir,"gate_decision.json"),gates)
        write_json(os.path.join(args.outdir,"execution_receipt.json"),{"run_id":run_id,"mode":args.mode,"receipts":receipts})
        return 1

    # 2) ESLint sensor (optional)
    eslint_sensor_root=os.path.join(args.root,"mbml_sensors","eslint")
    eslint_runner=os.path.join(eslint_sensor_root,"run_eslint.sh")
    sensor_rows=os.path.join(args.outdir,"eslint_sensor_rows.ndjson")
    ulvrs_eslint=os.path.join(args.outdir,"ulvrs_eslint_rows.ndjson")

    if os.path.exists(eslint_runner):
        # run adapter; it will emit an error-row if eslint missing
        rc,so,se=run(["bash", eslint_runner, sensor_rows, args.workspace])
        receipts.append({"step":"eslint_sensor","rc":rc,"stderr":se.strip()})
        # wrap into ULVRS
        rc2,so2,se2=run(["python3", wrap_eslint, sensor_rows, ulvrs_eslint, run_id, args.run_class])
        receipts.append({"step":"eslint_wrap_ulvrs","rc":rc2,"stderr":se2.strip()})
        if rc!=0 or rc2!=0:
            gates["reasons"].append("ESLint sensor degraded")
    else:
        gates["reasons"].append("ESLint sensor adapter missing")

    # 3) Drift diff vs baseline (run events)
    diff_out=os.path.join(args.outdir,"ulvrs_diff.ndjson")
    rc,so,se=run(["python3", diff, args.baseline, bts_ulvrs, diff_out, run_id, args.run_class])
    receipts.append({"step":"diff_engine","rc":rc,"stderr":se.strip()})
    if rc!=0:
        gates["status"]="FAIL"
        gates["reasons"].append("Diff engine failed")
    else:
        # gate: no changed rows allowed for baseline run_event corpus by default
        changed=0
        with open(diff_out,"r",encoding="utf-8") as f:
            for line in f:
                try:
                    r=json.loads(line)
                except Exception:
                    continue
                if r.get("row_type")=="diff_event" and r.get("identity",{}).get("diff_kind")=="changed":
                    changed+=1
        if changed>gates["thresholds"]["max_changed_rows"]:
            gates["status"]="FAIL"
            gates["reasons"].append(f"Drift: changed_rows={changed} > {gates['thresholds']['max_changed_rows']}")
        else:
            gates["status"]="PASS" if not gates["reasons"] else "PASS_WITH_WARNINGS"
            gates["metrics"]={"changed_rows":changed}

    write_json(os.path.join(args.outdir,"gate_decision.json"),gates)
    write_json(os.path.join(args.outdir,"execution_receipt.json"),{"run_id":run_id,"mode":args.mode,"run_class":args.run_class,"receipts":receipts,"artifacts":{
        "bts_ulvrs": bts_ulvrs,
        "eslint_sensor_rows": sensor_rows,
        "eslint_ulvrs": ulvrs_eslint,
        "diff": diff_out,
        "gate_decision": os.path.join(args.outdir,"gate_decision.json")
    }})
    return 0 if gates["status"] in ("PASS","PASS_WITH_WARNINGS") else 2

if __name__=="__main__":
    raise SystemExit(main())

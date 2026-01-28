#!/usr/bin/env python3
"""Wrap MBML ESLint sensor rows into ULVRS lint_violation rows.
Input is NDJSON of 'lint_violation' rows (sensor-level) OR single error row.
Output is ULVRS NDJSON.
Usage:
  wrap_eslint_ulvrs.py <in_sensor_rows.ndjson> <out_ulvrs_rows.ndjson> [run_id] [run_classification]
"""
import json, sys, time, hashlib, uuid

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def main():
    if len(sys.argv) < 3:
        print("USAGE: wrap_eslint_ulvrs.py <in.ndjson> <out.ndjson> [run_id] [run_classification]", file=sys.stderr)
        return 2
    in_path=sys.argv[1]
    out_path=sys.argv[2]
    run_id=sys.argv[3] if len(sys.argv) > 3 else str(uuid.uuid4())
    run_class=sys.argv[4] if len(sys.argv) > 4 else "reference"

    with open(in_path,"r",encoding="utf-8") as f_in, open(out_path,"w",encoding="utf-8") as f_out:
        for line in f_in:
            line=line.strip()
            if not line:
                continue
            try:
                r=json.loads(line)
            except Exception:
                continue
            # sensor row already has identity/location/finding/etc; wrap as payload
            fp_src=json.dumps(r, sort_keys=True, ensure_ascii=False)
            row={
                "row_id": r.get("hashes",{}).get("fingerprint") or sha256_text(fp_src),
                "row_type": "lint_violation",
                "source": {"system":"mbml","artifact":"eslint_sensor_rows","path": in_path},
                "identity": r.get("identity",{}),
                "payload": r,
                "context": r.get("context",{"intent":None,"constraints":[],"execution_mode":"analysis-only","quality_target":None}),
                "provenance": {"run_id": run_id, "phase": "ESLINT_SENSOR", "run_classification": run_class, "evidence_refs": []},
                "timestamps": {"created_utc": now(), "observed_utc": None},
                "hashes": {"fingerprint": r.get("hashes",{}).get("fingerprint") or sha256_text(fp_src), "content_sha256": sha256_text(line)}
            }
            f_out.write(json.dumps(row, ensure_ascii=False)+"\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

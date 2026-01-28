#!/usr/bin/env python3
"""Emit ULVRS run_event rows from MetaBlooms BTS ndjson ledger (append-only).
Usage:
  emit_ulvrs_from_bts.py <bts_ledger.ndjson> <out_rows.ndjson> [run_id] [run_classification]
"""
import json, sys, time, hashlib, uuid

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def main():
    if len(sys.argv) < 3:
        print("USAGE: emit_ulvrs_from_bts.py <bts_ledger.ndjson> <out_rows.ndjson> [run_id] [run_classification]", file=sys.stderr)
        return 2
    bts_path=sys.argv[1]
    out_path=sys.argv[2]
    run_id=sys.argv[3] if len(sys.argv) > 3 else str(uuid.uuid4())
    run_class=sys.argv[4] if len(sys.argv) > 4 else "reference"

    with open(bts_path,"r",encoding="utf-8") as f_in, open(out_path,"w",encoding="utf-8") as f_out:
        for line in f_in:
            line=line.strip()
            if not line:
                continue
            try:
                rec=json.loads(line)
            except Exception:
                continue
            phase=rec.get("phase","unknown")
            payload=rec.get("payload",{})
            ts=rec.get("ts") or now()

            fp_src=f"{phase}|{json.dumps(payload, sort_keys=True, ensure_ascii=False)}|{ts}"
            row={
                "row_id": sha256_text(fp_src),
                "row_type": "run_event",
                "source": {"system":"metablooms","artifact":"bts_ledger","path": bts_path},
                "identity": {"event_type": phase},
                "payload": {"bts": rec},
                "context": {"intent": None, "constraints": [], "execution_mode": "analysis-only", "quality_target": None},
                "provenance": {"run_id": run_id, "phase": phase, "run_classification": run_class, "evidence_refs": []},
                "timestamps": {"created_utc": ts, "observed_utc": ts},
                "hashes": {"fingerprint": sha256_text(fp_src), "content_sha256": sha256_text(line)}
            }
            f_out.write(json.dumps(row, ensure_ascii=False)+"\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

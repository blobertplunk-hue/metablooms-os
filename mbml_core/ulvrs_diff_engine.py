#!/usr/bin/env python3
"""ULVRS Diff Engine (v1)
Computes row-level diffs between two ULVRS NDJSON files using row_id as key.
Emits ULVRS diff_event rows:
  - added
  - removed
  - changed (payload hash differs)
Usage:
  ulvrs_diff_engine.py <old.ndjson> <new.ndjson> <out_diff.ndjson> [run_id] [run_classification]
"""
import json, sys, time, hashlib, uuid

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def load_map(path):
    m={}
    with open(path,"r",encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            try:
                r=json.loads(line)
            except Exception:
                continue
            rid=r.get("row_id")
            if not rid: continue
            m[rid]=r
    return m

def content_hash(row):
    # hash stable serialization of payload+identity+context
    base={
        "row_type": row.get("row_type"),
        "identity": row.get("identity"),
        "payload": row.get("payload"),
        "context": row.get("context"),
        "provenance": row.get("provenance")
    }
    return sha256_text(json.dumps(base, sort_keys=True, ensure_ascii=False))

def main():
    if len(sys.argv) < 4:
        print("USAGE: ulvrs_diff_engine.py <old.ndjson> <new.ndjson> <out.ndjson> [run_id] [run_classification]", file=sys.stderr)
        return 2
    old_path=sys.argv[1]
    new_path=sys.argv[2]
    out_path=sys.argv[3]
    run_id=sys.argv[4] if len(sys.argv) > 4 else str(uuid.uuid4())
    run_class=sys.argv[5] if len(sys.argv) > 5 else "reference"

    old=load_map(old_path)
    new=load_map(new_path)

    old_ids=set(old.keys())
    new_ids=set(new.keys())

    added=list(new_ids-old_ids)
    removed=list(old_ids-new_ids)
    common=list(old_ids & new_ids)

    with open(out_path,"w",encoding="utf-8") as f_out:
        for rid in sorted(added):
            r=new[rid]
            ev={
                "row_id": sha256_text("added|"+rid),
                "row_type":"diff_event",
                "source":{"system":"mbml","artifact":"ulvrs_diff","path": out_path},
                "identity":{"diff_kind":"added","target_row_id":rid},
                "payload":{"new": r, "old": None},
                "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only","quality_target":None},
                "provenance":{"run_id":run_id,"phase":"DIFF","run_classification":run_class,"evidence_refs":[old_path,new_path]},
                "timestamps":{"created_utc":now(),"observed_utc":None},
                "hashes":{"fingerprint":sha256_text("added|"+rid),"content_sha256":content_hash(r)}
            }
            f_out.write(json.dumps(ev, ensure_ascii=False)+"\n")

        for rid in sorted(removed):
            r=old[rid]
            ev={
                "row_id": sha256_text("removed|"+rid),
                "row_type":"diff_event",
                "source":{"system":"mbml","artifact":"ulvrs_diff","path": out_path},
                "identity":{"diff_kind":"removed","target_row_id":rid},
                "payload":{"new": None, "old": r},
                "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only","quality_target":None},
                "provenance":{"run_id":run_id,"phase":"DIFF","run_classification":run_class,"evidence_refs":[old_path,new_path]},
                "timestamps":{"created_utc":now(),"observed_utc":None},
                "hashes":{"fingerprint":sha256_text("removed|"+rid),"content_sha256":content_hash(r)}
            }
            f_out.write(json.dumps(ev, ensure_ascii=False)+"\n")

        for rid in sorted(common):
            o=old[rid]; n=new[rid]
            if content_hash(o)!=content_hash(n):
                ev={
                    "row_id": sha256_text("changed|"+rid),
                    "row_type":"diff_event",
                    "source":{"system":"mbml","artifact":"ulvrs_diff","path": out_path},
                    "identity":{"diff_kind":"changed","target_row_id":rid},
                    "payload":{"new": n, "old": o},
                    "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only","quality_target":None},
                    "provenance":{"run_id":run_id,"phase":"DIFF","run_classification":run_class,"evidence_refs":[old_path,new_path]},
                    "timestamps":{"created_utc":now(),"observed_utc":None},
                    "hashes":{"fingerprint":sha256_text("changed|"+rid),"content_sha256":sha256_text(content_hash(o)+content_hash(n))}
                }
                f_out.write(json.dumps(ev, ensure_ascii=False)+"\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

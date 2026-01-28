#!/usr/bin/env python3
"""Combine multiple lint_violation ULVRS streams into consensus/conflict rows."""
import json, sys, hashlib, time
def now(): return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
def sha(t): return hashlib.sha256(t.encode()).hexdigest()
def load(p):
    rows=[]
    with open(p) as f:
        for l in f:
            try: rows.append(json.loads(l))
            except: pass
    return rows
def main():
    if len(sys.argv)<4:
        print("USAGE: lint_consensus_engine.py <eslint.ndjson> <pylint.ndjson> <out.ndjson>")
        return 2
    e=load(sys.argv[1]); p=load(sys.argv[2])
    out=sys.argv[3]
    key=lambda r:(r.get("identity",{}).get("path"),r.get("identity",{}).get("line"))
    emap={key(r):r for r in e}; pmap={key(r):r for r in p}
    with open(out,"w") as o:
        for k in set(emap)|set(pmap):
            kind="consensus" if k in emap and k in pmap else "conflict"
            row={
              "row_type":"lint_consensus" if kind=="consensus" else "lint_conflict",
              "identity":{"location":k},
              "payload":{"eslint":emap.get(k),"pylint":pmap.get(k)},
              "timestamps":{"created_utc":now()},
              "hashes":{"fingerprint":sha(kind+str(k))}
            }
            o.write(json.dumps(row)+"\n")
    return 0
if __name__=="__main__": raise SystemExit(main())

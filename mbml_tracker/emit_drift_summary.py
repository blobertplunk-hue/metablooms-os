#!/usr/bin/env python3
"""Emit drift summary rows from ULVRS diff NDJSON.
Outputs a compact JSON summary for dashboards and gates.
"""
import json, sys, time
def main():
    if len(sys.argv)<3:
        print("USAGE: emit_drift_summary.py <diff.ndjson> <out.json>", file=sys.stderr)
        return 2
    diff=sys.argv[1]; out=sys.argv[2]
    s={"added":0,"removed":0,"changed":0}
    with open(diff,"r",encoding="utf-8") as f:
        for line in f:
            try:
                r=json.loads(line)
            except Exception:
                continue
            k=r.get("identity",{}).get("diff_kind")
            if k in s: s[k]+=1
    s["generated_utc"]=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(out,"w",encoding="utf-8") as f:
        json.dump(s,f,indent=2)
    return 0
if __name__=="__main__":
    raise SystemExit(main())

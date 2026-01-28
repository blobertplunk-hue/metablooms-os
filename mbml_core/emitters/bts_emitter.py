#!/usr/bin/env python3
import json, sys, time, hashlib, uuid

def fp(s): return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

rows=[]
for line in sys.stdin:
    if not line.strip(): continue
    r=json.loads(line)
    rows.append({
      "row_id":str(uuid.uuid4()),
      "row_type":"run_event",
      "source":{"system":"bts","artifact":"ledger"},
      "identity":{"phase":r.get("phase")},
      "payload":r.get("payload"),
      "context":{"intent":None,"constraints":[],"execution_mode":"derived","quality_target":None},
      "provenance":{"run_id":"unknown","phase":r.get("phase"),"run_classification":"reference","evidence_refs":[]},
      "timestamps":{"created_utc":r.get("ts"),"observed_utc":None},
      "hashes":{"fingerprint":fp(json.dumps(r,sort_keys=True))}
    })

json.dump(rows, sys.stdout, indent=2)

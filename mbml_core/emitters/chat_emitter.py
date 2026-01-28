#!/usr/bin/env python3
import json, sys, time, hashlib, uuid

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def fp(s): return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()

# stdin: JSON array of {role, content, ts}
data=json.load(sys.stdin)
out=[]
for i,m in enumerate(data):
    row={
      "row_id":str(uuid.uuid4()),
      "row_type":"chat_turn",
      "source":{"system":"chat","artifact":"transcript"},
      "identity":{"speaker":m.get("role"),"turn_index":i},
      "payload":{"text":m.get("content")},
      "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only","quality_target":None},
      "provenance":{"run_id":"unknown","phase":"P?","run_classification":"reference","evidence_refs":[]},
      "timestamps":{"created_utc":m.get("ts") or now(),"observed_utc":None},
      "hashes":{"fingerprint":fp((m.get("content") or "")+str(i))}
    }
    out.append(row)

json.dump(out, sys.stdout, indent=2)

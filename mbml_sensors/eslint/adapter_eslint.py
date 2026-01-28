#!/usr/bin/env python3
"""MetaBlooms MBML ESLint Sensor Adapter (v1)
- Runs ESLint if available.
- Emits ULVRS rows (lint_violation) as NDJSON.
- Read-only: does not modify source files.
"""
import json, subprocess, sys, os, hashlib, time

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256_text(t: str) -> str:
    import hashlib
    return hashlib.sha256(t.encode("utf-8", errors="ignore")).hexdigest()

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout, p.stderr

def main():
    if len(sys.argv) < 3:
        print("USAGE: adapter_eslint.py <out_ndjson> <file_or_dir> [more...]", file=sys.stderr)
        return 2
    out_path = sys.argv[1]
    targets = sys.argv[2:]
    eslint = os.environ.get("MBML_ESLINT_BIN", "eslint")
    # Use JSON formatter for machine parsing; ESLint v8 supports -f json
    cmd = [eslint, "-f", "json"] + targets
    rc, stdout, stderr = run(cmd)
    if rc != 0 and not stdout:
        # Degraded: cannot run eslint (missing binary or runtime error)
        row = {
            "row_type":"lint_violation",
            "identity":{"tool":"eslint","rule_id":"MBML-ESLINT-RUN-FAILED","language":"js"},
            "location":{"artifact":";".join(targets),"line":0,"column":0,"span":None},
            "finding":{"message":stderr.strip() or "eslint failed with no output","category":"tooling","severity":"error"},
            "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only"},
            "quality_impact":{"estimated":-10,"historical_false_positive_rate":0.0},
            "resolution":{"suggested_fix":"Provide eslint in PATH or set MBML_ESLINT_BIN","auto_fixable":False},
            "hashes":{"fingerprint":sha256_text("MBML-ESLINT-RUN-FAILED:"+(";".join(targets)))}
        }
        with open(out_path,"w",encoding="utf-8") as f:
            f.write(json.dumps(row)+"\n")
        return 0
    try:
        data = json.loads(stdout)
    except Exception as e:
        row = {
            "row_type":"lint_violation",
            "identity":{"tool":"eslint","rule_id":"MBML-ESLINT-NONJSON","language":"js"},
            "location":{"artifact":";".join(targets),"line":0,"column":0,"span":None},
            "finding":{"message":"eslint output not JSON: "+str(e),"category":"tooling","severity":"error"},
            "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only"},
            "quality_impact":{"estimated":-10,"historical_false_positive_rate":0.0},
            "resolution":{"suggested_fix":"Ensure eslint supports -f json","auto_fixable":False},
            "hashes":{"fingerprint":sha256_text("MBML-ESLINT-NONJSON:"+(";".join(targets)))}
        }
        with open(out_path,"w",encoding="utf-8") as f:
            f.write(json.dumps(row)+"\n")
        return 0

    # ESLint JSON is list of file results
    rows = []
    for file_result in data:
        file_path = file_result.get("filePath") or file_result.get("filePath", "")
        messages = file_result.get("messages", []) or []
        for m in messages:
            rule_id = m.get("ruleId") or "unknown"
            sev = m.get("severity", 1)
            severity = "warn" if sev == 1 else "error"
            line = int(m.get("line") or 0)
            col = int(m.get("column") or 0)
            msg = m.get("message") or ""
            cat = "style"  # eslint mixes style/bug; refine later via rule map
            fingerprint_src = f"{file_path}|{rule_id}|{line}|{col}|{msg}"
            row = {
                "row_type":"lint_violation",
                "identity":{"tool":"eslint","rule_id":rule_id,"language":"js"},
                "location":{"artifact":file_path,"line":line,"column":col,"span":None},
                "finding":{"message":msg,"category":cat,"severity":severity},
                "context":{"intent":None,"constraints":[],"execution_mode":"analysis-only"},
                "quality_impact":{"estimated":-1 if severity=='warn' else -3,"historical_false_positive_rate":0.0},
                "resolution":{"suggested_fix":None,"auto_fixable":False},
                "hashes":{"fingerprint":sha256_text(fingerprint_src)}
            }
            rows.append(row)

    with open(out_path,"w",encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r)+"\n")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

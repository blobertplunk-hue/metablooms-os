#!/usr/bin/env python3
"""P9.5 BTS META-AUDIT (non-blocking, evidence-backed)
Usage:
  p95_bts_meta_audit.py --bts <bts.ndjson> --outdir <outdir> [--run-id <id>]
Emits:
  - bts_meta_audit.report.json
  - process_improvement_candidates.json
  - recommended_invariant_changes.json
"""
import argparse, json, os, re, time, uuid
from datetime import datetime

def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def load_bts(path):
    rows=[]
    with open(path,'r',encoding='utf-8') as f:
        for i,line in enumerate(f):
            line=line.strip()
            if not line: continue
            try:
                r=json.loads(line)
                r['_bts_index']=i
                rows.append(r)
            except Exception:
                continue
    return rows

def flatten(obj):
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)

def parse_ts(ts):
    try:
        return datetime.fromisoformat(ts.replace("Z","+00:00"))
    except Exception:
        return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--bts', required=True)
    ap.add_argument('--outdir', required=True)
    ap.add_argument('--run-id', default=None)
    args=ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)
    run_id=args.run_id or str(uuid.uuid4())

    rows=load_bts(args.bts)
    texts=[(r.get('phase',''), flatten(r.get('payload',{})), r['_bts_index']) for r in rows]

    # Pattern frequency
    token_re=re.compile(r"[A-Za-z][A-Za-z0-9_\-]{2,}")
    freq={}
    for ph,txt,idx in texts:
        for t in token_re.findall(ph+" "+txt):
            t=t.lower()
            freq[t]=freq.get(t,0)+1
    top_tokens=sorted(freq.items(), key=lambda x:x[1], reverse=True)[:40]

    # Phase cost (delta seconds between entries)
    times=[]
    for r in rows:
        ts=parse_ts(r.get('ts',''))
        if ts:
            times.append((ts, r.get('phase',''), r['_bts_index']))
    times.sort(key=lambda x:x[0])
    deltas=[]
    per_phase={}
    for (t1,ph1,i1),(t2,ph2,i2) in zip(times, times[1:]):
        dt=(t2-t1).total_seconds()
        deltas.append(dt)
        per_phase.setdefault(ph2,[]).append(dt)
    phase_cost={
        "total_entries":len(rows),
        "delta_seconds_summary":{
            "count":len(deltas),
            "min":min(deltas) if deltas else 0,
            "max":max(deltas) if deltas else 0,
            "mean":(sum(deltas)/len(deltas)) if deltas else 0
        },
        "per_phase_mean_seconds":{k:(sum(v)/len(v)) for k,v in per_phase.items() if v}
    }

    # Governance misuse
    misuse_terms=["fail-closed","fail_closed","refuse","blocked","cannot","not possible","policy"]
    misuse_hits=[]
    for ph,txt,idx in texts:
        l=(ph+" "+txt).lower()
        if any(term in l for term in misuse_terms):
            misuse_hits.append({"bts_index":idx,"phase":ph,"snippet":l[:220]})
    governance_misuse={"hit_count":len(misuse_hits),"hits":misuse_hits[:10]}

    # Tooling friction
    tool_terms=["not installed","missing","unavailable","command -v","gated","typing_disabled","typing_config_missing"]
    tool_hits=[]
    for ph,txt,idx in texts:
        l=(ph+" "+txt).lower()
        if any(term in l for term in tool_terms):
            tool_hits.append({"bts_index":idx,"phase":ph,"snippet":l[:220]})
    tooling_friction={"hit_count":len(tool_hits),"hits":tool_hits[:10]}

    # Human friction (from BTS only; chat text not included)
    human_terms=["pissed","annoy","bullshit","ass","hate","frustrat","stop","pain"]
    human_hits=[]
    for ph,txt,idx in texts:
        l=(ph+" "+txt).lower()
        if any(term in l for term in human_terms):
            human_hits.append({"bts_index":idx,"phase":ph,"snippet":l[:220]})
    human_friction={"hit_count":len(human_hits),"hits":human_hits[:10]}

    findings=[]
    warnings=[]

    if len(rows) < 25:
        warnings.append("BTS ledger is short (limited scope); meta-audit confidence limited to observed entries.")
        findings.append({
            "id":"FIND_SCOPE_001",
            "severity":"MEDIUM",
            "title":"Limited BTS corpus in scope",
            "evidence":{"entry_count":len(rows)},
            "impact":"Meta-audit cannot infer long-run friction patterns from a short ledger.",
            "fix":"Ensure BTS is emitted for every phase across the full chat/run; aggregate all per-run ledgers before P9.5."
        })

    if governance_misuse["hit_count"]>0:
        findings.append({
            "id":"FIND_GOV_001",
            "severity":"HIGH",
            "title":"Blocking language detected in BTS artifacts",
            "evidence":{"hit_count":governance_misuse["hit_count"],"examples":governance_misuse["hits"]},
            "impact":"May indicate fail-closed/refusal posture being encoded into telemetry.",
            "fix":"Enforce invariant: tool absence ⇒ mode downgrade + continue; fail-closed only for unsafe/disallowed."
        })
    else:
        warnings.append("No blocking/fail-closed language observed in BTS entries scanned.")

    if tooling_friction["hit_count"]>0:
        findings.append({
            "id":"FIND_TOOL_001",
            "severity":"LOW",
            "title":"Tooling friction signals present (gates/degraded paths)",
            "evidence":{"hit_count":tooling_friction["hit_count"],"examples":tooling_friction["hits"]},
            "impact":"Tool availability decisions can feel like stalling unless substitutes are auto-selected and recorded.",
            "fix":"Log chosen substitute explicitly in BTS; prefer auto-substitution when tool missing."
        })

    candidates=[{
        "id":"IMP_P95_001",
        "priority":"P0",
        "proposal":"Insert mandatory P9.5 BTS_META_AUDIT after P9 and before P10; always emit 3 artifacts.",
        "rationale":"Forces cross-BTS aggregation before recursion; makes improvements evidence-driven.",
        "evidence_refs":[{"bts_index":rows[0]['_bts_index'],"phase":rows[0].get('phase','')}] if rows else []
    }]

    invariants=[
        {
            "id":"INV_P95_REQUIRED",
            "change_type":"ADD",
            "text":"P10 RECURSION MUST NOT execute unless P9.5 BTS_META_AUDIT artifacts exist for the same run_id.",
            "justification":"Ensures recursion is data-driven from BTS, not intuition.",
            "evidence_refs":[{"bts_index":rows[0]['_bts_index'],"phase":rows[0].get('phase','')}] if rows else []
        },
        {
            "id":"INV_P95_NONBLOCKING",
            "change_type":"ADD",
            "text":"P9.5 BTS_META_AUDIT is advisory-only and MUST NOT block execution or rewrite history.",
            "justification":"Meta-audit must not become a new gating failure mode.",
            "evidence_refs":[]
        },
        {
            "id":"INV_ARTIFACT_FIRST_BTS",
            "change_type":"ADD",
            "text":"Every phase MUST emit at least one artifact or delta proposal; narrative-only steps are invalid.",
            "justification":"Reduces explanation-only loops; keeps momentum while staying honest.",
            "evidence_refs":[]
        }
    ]

    report={
        "phase":"P9.5",
        "run_id":run_id,
        "inputs":{
            "bts_paths":[args.bts],
            "entry_count":len(rows),
            "coverage_note":"Scan covers only entries present in provided BTS file; no external ledgers assumed."
        },
        "summary":{"overall":"PASS_WITH_WARNINGS" if warnings else "PASS","key_warnings":warnings},
        "analyses":{
            "pattern_frequency":{"top_tokens":top_tokens},
            "phase_cost":phase_cost,
            "governance_misuse":governance_misuse,
            "tooling_friction":tooling_friction,
            "human_friction":human_friction
        },
        "findings":findings,
        "timestamps":{"created_utc":now()}
    }

    def dump(name,obj):
        path=os.path.join(args.outdir,name)
        with open(path,'w',encoding='utf-8') as f:
            json.dump(obj,f,indent=2,ensure_ascii=False)
        return path

    p_report=dump("bts_meta_audit.report.json", report)
    p_cand=dump("process_improvement_candidates.json", {"run_id":run_id,"candidates":candidates,"timestamps":{"created_utc":now()}})
    p_inv=dump("recommended_invariant_changes.json", {"run_id":run_id,"invariants":invariants,"timestamps":{"created_utc":now()}})

    print(json.dumps({"run_id":run_id,"artifacts":[p_report,p_cand,p_inv]}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

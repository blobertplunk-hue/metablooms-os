# build_quality_timeseries.py (stub)
# Reads row ledger or BTS ledger and emits timeseries for dashboard.
import json, csv, pathlib, re, datetime

def iter_ndjson(path):
    for line in pathlib.Path(path).read_text(encoding="utf-8", errors="ignore").splitlines():
        line=line.strip()
        if not line: continue
        yield json.loads(line)

def detect_artifacts(text):
    return len(re.findall(r"/mnt/data/[^\s\]]+", text))

def detect_missing_mode(text):
    low=text.lower()
    if any(k in low for k in ["can't","cannot","fail-closed","unsafe","disallowed"]):
        return 0 if "mode:" in low else 1
    return 0

def detect_deflection(text):
    low=text.lower()
    return 1 if any(k in low for k in ["as an ai","policy","training","fine-tuning"]) else 0

def ceremony_ratio(text):
    low=text.lower()
    ceremonials=sum(low.count(k.lower()) for k in ["p0","p1","mpp","phase"])
    return ceremonials / max(len(text.split()),1)

def score_proxy(text):
    # small proxy: artifacts + mode - deflection - ceremony
    a=detect_artifacts(text)
    m=0 if detect_missing_mode(text)==1 else 1
    d=1-detect_deflection(text)
    c=1.0 - min(ceremony_ratio(text), 1.0)
    base = min(a/5,1.0)*0.4 + m*0.2 + d*0.3 + c*0.1
    return int(round(base*100))

def build(rows_path, out_json, out_csv):
    points=[]
    if rows_path and pathlib.Path(rows_path).exists():
        for r in iter_ndjson(rows_path):
            text = r.get("content",{}).get("raw","")
            turn = r.get("timestamps",{}).get("observed_utc") or r.get("timestamps",{}).get("created_utc")
            points.append({
                "turn_utc": turn,
                "row_id": r.get("row_id"),
                "score": score_proxy(text),
                "artifact_hits": detect_artifacts(text),
                "missing_mode": detect_missing_mode(text),
                "deflection": detect_deflection(text),
                "ceremony_ratio": ceremony_ratio(text)
            })
    pathlib.Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(out_json).write_text(json.dumps(points, indent=2), encoding="utf-8")
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w=csv.DictWriter(f, fieldnames=list(points[0].keys()) if points else ["turn_utc","row_id","score","artifact_hits","missing_mode","deflection","ceremony_ratio"])
        w.writeheader()
        for p in points:
            w.writerow(p)

if __name__ == "__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--rows", required=False, default="analysis/high_quality_replay/unified_rows.ndjson")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-csv", required=True)
    args=ap.parse_args()
    build(args.rows, args.out_json, args.out_csv)

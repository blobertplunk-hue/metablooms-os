#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS.LEDGER
# ECL_RESPONSIBILITY: Filter NDJSON ledger entries by key=value predicates; read-only.

import argparse, json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--where", action="append", default=[])
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    p = Path(a.ledger)
    if not p.exists():
        print(f"ERROR: ledger not found: {p}")
        return 2

    pred = {}
    for w in a.where:
        if "=" not in w:
            raise SystemExit(f"Invalid --where {w} (expected key=value)")
        k, v = w.split("=", 1)
        pred[k.strip()] = v.strip()

    matches = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        ok = True
        for k, v in pred.items():
            if str(obj.get(k)) != v:
                ok = False
                break
        if ok:
            print(json.dumps(obj, sort_keys=True))
            matches += 1
            if a.limit and matches >= a.limit:
                break

    print(json.dumps({"matches": matches}, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

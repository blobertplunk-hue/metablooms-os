#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS.LEDGER
# ECL_RESPONSIBILITY: Deterministically render NDJSON ledger entries; read-only.

import argparse, json
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--raw", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    p = Path(a.ledger)
    if not p.exists():
        print(f"ERROR: ledger not found: {p}")
        return 2

    n = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        n += 1
        if a.raw:
            print(line)
        else:
            try:
                print(json.dumps(json.loads(line), indent=2, sort_keys=True))
            except json.JSONDecodeError:
                print(line)
        if a.limit and n >= a.limit:
            break
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

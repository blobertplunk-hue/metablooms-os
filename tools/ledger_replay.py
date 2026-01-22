#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS.LEDGER
# ECL_RESPONSIBILITY: Provide deterministic summary over NDJSON ledger; read-only.

import argparse, json
from collections import Counter
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    a = ap.parse_args()

    p = Path(a.ledger)
    if not p.exists():
        print(f"ERROR: ledger not found: {p}")
        return 2

    events = Counter()
    statuses = Counter()
    total = 0
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        total += 1
        if "event" in obj:
            events[str(obj["event"])] += 1
        if "status" in obj:
            statuses[str(obj["status"])] += 1

    print(json.dumps({
        "total": total,
        "events_top": events.most_common(25),
        "statuses": dict(statuses),
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

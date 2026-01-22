"""
MetaBlooms Invariant Regression Alerts
- Baseline is explicit (canonical/baseline_invariants.json) if present,
  else previous turn receipt.
Fail-closed:
    - If baseline cannot be determined -> exit(2)
    - If regressions found -> exit(3)
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

def _load_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def discover_turn_receipts(os_root: Path) -> list[Path]:
    turns_dir = os_root / "ledgers" / "turns"
    if not turns_dir.exists():
        return []
    recs = []
    for d in turns_dir.iterdir():
        r = d / "boot_receipt.json"
        if d.is_dir() and r.exists():
            recs.append(r)
    recs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return recs

def main(argv):
    if len(argv) < 2:
        print("USAGE: python -m metablooms.tools.regression_alerts <os_root>", file=sys.stderr)
        return 2
    os_root = Path(argv[1])

    baseline_file = os_root / "metablooms" / "canonical" / "baseline_invariants.json"
    if baseline_file.exists():
        baseline = set(_load_json(baseline_file).get("baseline_invariants", []) or [])
        baseline_src = str(baseline_file)
    else:
        recs = discover_turn_receipts(os_root)
        if len(recs) < 2:
            print("BASELINE_NOT_FOUND (need baseline file or >=2 turn receipts)", file=sys.stderr)
            return 2
        baseline = set(_load_json(recs[1]).get("invariants_loaded", []) or [])
        baseline_src = str(recs[1])

    recs = discover_turn_receipts(os_root)
    if not recs:
        print("NO_LATEST_TURN", file=sys.stderr)
        return 2
    cur = _load_json(recs[0])
    cur_set = set(cur.get("invariants_loaded", []) or [])

    missing = sorted(baseline - cur_set)
    if missing:
        print("INVARIANT_REGRESSION_DETECTED")
        print(f"Baseline: {baseline_src}")
        print(f"Current : {recs[0]}")
        print("Missing invariants:")
        for x in missing:
            print(f" - {x}")
        return 3

    print("NO_REGRESSIONS")
    print(f"Baseline: {baseline_src}")
    print(f"Current : {recs[0]}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

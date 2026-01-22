"""
MetaBlooms CLI: What changed since last turn?
- Discovers latest two turn receipts and emits a concise summary.
Fail-closed:
    - If <2 turns with receipts -> exit(2)
"""
from __future__ import annotations
import json
from pathlib import Path
import sys
from datetime import datetime

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

def diff_receipts(prev: dict, cur: dict) -> dict:
    prev_inv = set(prev.get("invariants_loaded", []) or [])
    cur_inv  = set(cur.get("invariants_loaded", []) or [])

    added_inv = sorted(cur_inv - prev_inv)
    removed_inv = sorted(prev_inv - cur_inv)

    keys = ["boot_mode", "state_mode"]
    changed = []
    for k in keys:
        if prev.get(k) != cur.get(k):
            changed.append({"key": k, "before": prev.get(k), "after": cur.get(k)})

    return {
        "meta": {
            "prev_turn": prev.get("turn_id", "UNKNOWN_PREV"),
            "cur_turn": cur.get("turn_id", "UNKNOWN_CUR"),
            "created_utc": datetime.utcnow().isoformat() + "Z"
        },
        "added": {"invariants_loaded": added_inv},
        "removed": {"invariants_loaded": removed_inv},
        "changed": {"receipt_fields": changed}
    }

def main(argv):
    if len(argv) < 2:
        print("USAGE: python -m metablooms.tools.what_changed <os_root>", file=sys.stderr)
        return 2
    os_root = Path(argv[1])
    recs = discover_turn_receipts(os_root)
    if len(recs) < 2:
        print("NEED_2_TURNS_WITH_RECEIPTS", file=sys.stderr)
        return 2

    cur = _load_json(recs[0])
    prev = _load_json(recs[1])
    d = diff_receipts(prev, cur)

    print("WHAT_CHANGED_SINCE_LAST_TURN")
    print(f"Prev: {d['meta']['prev_turn']}")
    print(f"Cur : {d['meta']['cur_turn']}")
    print("")
    print("Added invariants:")
    print(" - " + "\n - ".join(d['added']['invariants_loaded']) if d['added']['invariants_loaded'] else " (none)")
    print("Removed invariants:")
    print(" - " + "\n - ".join(d['removed']['invariants_loaded']) if d['removed']['invariants_loaded'] else " (none)")
    print("Changed receipt fields:")
    if not d["changed"]["receipt_fields"]:
        print(" (none)")
    else:
        for c in d["changed"]["receipt_fields"]:
            print(f" - {c['key']}: {c['before']} -> {c['after']}")

    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

from pathlib import Path
import json

def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))

def run_gate(ctx):
    turns = ctx.os_root / "ledgers" / "turns"
    receipts = []
    if not turns.exists():
        return
    for d in turns.iterdir():
        r = d / "boot_receipt.json"
        if d.is_dir() and r.exists():
            receipts.append(r)
    if len(receipts) < 2:
        return
    receipts.sort(key=lambda p: p.stat().st_mtime)
    prev = _read_json(receipts[-2])
    cur  = _read_json(receipts[-1])
    if "turn_index" not in prev or "turn_index" not in cur:
        raise RuntimeError("P1_FAIL: TURN_INDEX_MISSING")
    if int(cur["turn_index"]) != int(prev["turn_index"]) + 1:
        raise RuntimeError("P1_FAIL: TURN_INDEX_DISCONTINUITY")

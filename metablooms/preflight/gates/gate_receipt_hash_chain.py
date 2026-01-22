
from pathlib import Path
import json, hashlib

def _hash(obj: dict) -> str:
    data = json.dumps(obj, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def run_gate(ctx):
    turns_dir = ctx.os_root / "ledgers" / "turns"
    receipts = []
    for d in turns_dir.iterdir():
        r = d / "boot_receipt.json"
        if d.is_dir() and r.exists():
            receipts.append(r)
    if len(receipts) < 2:
        return

    receipts.sort(key=lambda p: p.stat().st_mtime)
    prev = json.loads(receipts[-2].read_text(encoding="utf-8"))
    cur  = json.loads(receipts[-1].read_text(encoding="utf-8"))

    expected_prior = prev.get("receipt_hash")
    if expected_prior is None:
        raise RuntimeError("P0_FAIL: PRIOR_RECEIPT_HASH_MISSING")

    if cur.get("prior_receipt_hash") != expected_prior:
        raise RuntimeError("P0_FAIL: RECEIPT_CHAIN_BROKEN")

    if cur.get("receipt_hash") != _hash({k:v for k,v in cur.items() if k != "receipt_hash"}):
        raise RuntimeError("P0_FAIL: RECEIPT_HASH_INVALID")

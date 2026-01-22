
from pathlib import Path
import json, hashlib

def hash_receipt(receipt: dict) -> str:
    data = json.dumps(receipt, sort_keys=True).encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def chain_receipt(receipt: dict, prior_hash: str | None) -> dict:
    receipt["prior_receipt_hash"] = prior_hash
    receipt["receipt_hash"] = hash_receipt(receipt)
    return receipt

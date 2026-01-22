import os
import json

METAGATE_ID = "METAGATE.P0.ZROOT.SENTINEL.MATCH.V1"
SENTINEL = "metablooms/diagnostics/zroot_sentinel_v1.json"


def evaluate(context: dict):
    """Requires sentinel exists and matches expected source hash provided in context."""
    os_root = context.get("os_root")
    expected = context.get("expected_source_zip_sha256")

    if not os_root:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["MISSING_CONTEXT:os_root"]}
    if not expected:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["MISSING_CONTEXT:expected_source_zip_sha256"]}

    p = os.path.join(os_root, SENTINEL)
    if not os.path.exists(p):
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"MISSING_SENTINEL:{SENTINEL}"]}

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"UNPARSEABLE_SENTINEL:{e}"]}

    if data.get("schema") != "zroot_sentinel_v1":
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["BAD_SCHEMA"]}

    actual = data.get("source_zip_sha256")
    if actual != expected:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"HASH_MISMATCH:{actual}!={expected}"]}

    return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}

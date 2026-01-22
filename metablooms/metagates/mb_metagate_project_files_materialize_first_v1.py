import os
import json

METAGATE_ID = "METAGATE.P0.PROJECT_FILES.MATERIALIZE_FIRST.V1"
BREADCRUMB = "metablooms/diagnostics/materialization_breadcrumb_v1.json"
REQUIRED_KEYS = ["schema", "source", "target", "ts", "outcome"]


def evaluate(context: dict):
    os_root = context.get("os_root")
    if not os_root:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["MISSING_CONTEXT:os_root"]}

    p = os.path.join(os_root, BREADCRUMB)
    if not os.path.exists(p):
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"MISSING_BREADCRUMB:{BREADCRUMB}"]}

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"UNPARSEABLE_BREADCRUMB:{e}"]}

    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"INVALID_BREADCRUMB_SCHEMA:{missing}"]}

    if data.get("schema") != "materialization_breadcrumb_v1":
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": [f"BAD_SCHEMA:{data.get('schema')}"]}

    return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}

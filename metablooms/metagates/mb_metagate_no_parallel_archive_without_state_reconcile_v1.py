import os
import json

METAGATE_ID = "METAGATE.P0.NO_PARALLEL_ARCHIVE_WITHOUT_STATE_RECONCILE.V1"
LOG = "metablooms/diagnostics/reconcile_attempts.ndjson"


def _has_reconcile_record(os_root: str, turn_id: str) -> bool:
    p = os.path.join(os_root, LOG)
    if not os.path.exists(p):
        return False
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("turn_id") == turn_id and rec.get("action") == "ARCHIVE_CREATE_REQUEST":
                return True
    return False


def evaluate(context: dict):
    os_root = context.get("os_root")
    turn_id = context.get("turn_id")
    op = context.get("operation")

    if not os_root or not turn_id or not op:
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["MISSING_CONTEXT:os_root/turn_id/operation"]}

    if op != "ARCHIVE_CREATE":
        return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}

    if not _has_reconcile_record(os_root, turn_id):
        return {"metagate_id": METAGATE_ID, "pass": False, "errors": ["NO_RECONCILIATION_EVIDENCE_FOR_ARCHIVE_CREATE"]}

    return {"metagate_id": METAGATE_ID, "pass": True, "errors": []}

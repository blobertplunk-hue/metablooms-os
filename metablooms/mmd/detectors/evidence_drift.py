"""
MMD DETECTOR: EVIDENCE_DRIFT

Compares hashes and version identifiers of bound external evidence
between prior and current runs to detect drift.
"""

def detect_evidence_drift(prior_items: list[dict], current_items: list[dict]) -> dict:
    drift = []
    prior_map = {it.get("item_id"): it for it in prior_items or []}
    for it in current_items or []:
        pid = it.get("item_id")
        if pid in prior_map:
            if it.get("content_hash") != prior_map[pid].get("content_hash"):
                drift.append({
                    "item_id": pid,
                    "type": "CONTENT_HASH_CHANGED"
                })
    return {
        "drift_detected": len(drift) > 0,
        "details": drift
    }

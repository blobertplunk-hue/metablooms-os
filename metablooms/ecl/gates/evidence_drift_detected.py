"""
ECL GATE: EVIDENCE_DRIFT_DETECTED

Enforces MDL-0003 (Evidence Lineage) and MDL-0004 (Mandatory Re-evaluation).

If upstream evidence bound to a prior promotion has materially changed
(hash mismatch, version change, or retraction), any subsequent promotion
or reuse MUST re-run SEE and MMD.

Fail-closed: detected drift without re-evaluation BLOCKS promotion.
"""

def enforce_evidence_drift(context: dict) -> dict | None:
    """
    Expected context fields:
      - prior_evidence_items: list[dict]
      - current_evidence_items: list[dict]
      - drift_detected: bool
      - reevaluated: bool
    """
    if context.get("drift_detected") and not context.get("reevaluated"):
        return {
            "action": "BLOCK",
            "owner": "MetaBlooms",
            "mdl": ["MDL-0003","MDL-0004"],
            "reason_code": "EVIDENCE_DRIFT_NOT_REEVALUATED"
        }
    return None

"""
ECL GATE: LINEAGE_REQUIRED_ON_RETRY

Enforces MDL-0003 (Evidence Lineage) and MDL-0004 (Mandatory Recursion).
If a prior promotion attempt for the same candidate resulted in BLOCK,
any subsequent retry MUST reference parent_evidence_id.

Fail-closed: retry without lineage BLOCKS.
"""

def enforce_lineage_required_on_retry(context: dict) -> dict | None:
    """
    context fields (expected):
      - is_retry: bool
      - prior_blocked: bool
      - parent_evidence_id: str | None
    Returns consequence dict on BLOCK, else None.
    """
    if context.get("is_retry") and context.get("prior_blocked"):
        if not context.get("parent_evidence_id"):
            return {
                "action": "BLOCK",
                "owner": "MetaBlooms",
                "mdl": ["MDL-0003", "MDL-0004"],
                "reason_code": "LINEAGE_REQUIRED_ON_RETRY"
            }
    return None

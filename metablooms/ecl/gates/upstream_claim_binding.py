"""
ECL GATE: UPSTREAM_CLAIM_BINDING

Enforces MDL-0003 (Evidence Lineage) and MDL-0001 (Consequence Binding).

If a promotion decision relies on upstream behavior, documentation,
policy semantics, or external guarantees, the Evidence Pack MUST
contain explicit External SEE items that bind the claim to sources.

Fail-closed: implicit upstream assumptions BLOCK promotion.
"""

def enforce_upstream_claim_binding(context: dict) -> dict | None:
    """
    Expected context fields:
      - relies_on_upstream_claims: bool
      - external_see_items: list[dict]
    """
    if context.get("relies_on_upstream_claims"):
        items = context.get("external_see_items") or []
        if not items:
            return {
                "action": "BLOCK",
                "owner": "MetaBlooms",
                "mdl": ["MDL-0003","MDL-0001"],
                "reason_code": "UPSTREAM_CLAIM_UNBOUND"
            }
        # require at least one HIGH-confidence primary source
        has_primary_high = any(
            it.get("confidence") == "HIGH" and it.get("source_type") in
            {"docs","release_notes","standard","security_advisory"}
            for it in items
        )
        if not has_primary_high:
            return {
                "action": "BLOCK",
                "owner": "MetaBlooms",
                "mdl": ["MDL-0003","MDL-0001"],
                "reason_code": "UPSTREAM_CLAIM_INSUFFICIENT_CONFIDENCE"
            }
    return None

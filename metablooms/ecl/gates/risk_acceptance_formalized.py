"""
ECL GATE: RISK_ACCEPTANCE_FORMALIZED

Enforces MDL-0006 (Explicit Risk Acceptance).

If a promotion would otherwise BLOCK and a waiver is applied,
the waiver MUST be:
- Explicitly declared
- Evidence-backed
- Owner-attributed
- Time-bounded

Expired or missing waivers BLOCK promotion automatically.
"""

def enforce_risk_acceptance(context: dict) -> dict | None:
    waiver = context.get("risk_acceptance")
    if not waiver:
        return None

    now = context.get("now")
    if waiver.get("expires_at") and waiver["expires_at"] < now:
        return {
            "action": "BLOCK",
            "owner": "MetaBlooms",
            "mdl": ["MDL-0006"],
            "reason_code": "RISK_ACCEPTANCE_EXPIRED"
        }

    required_fields = ["owner","justification","evidence_ids","expires_at"]
    for f in required_fields:
        if not waiver.get(f):
            return {
                "action": "BLOCK",
                "owner": "MetaBlooms",
                "mdl": ["MDL-0006"],
                "reason_code": "RISK_ACCEPTANCE_INCOMPLETE"
            }
    return None

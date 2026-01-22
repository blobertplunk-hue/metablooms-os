class PromotionBlocked(Exception):
    def __init__(self, consequence: dict):
        super().__init__(consequence.get("reason_code", "PROMOTION_BLOCKED"))
        self.consequence = consequence

def enforce_decision(decision: dict) -> dict:
    '''
    Own enforcement of consequence (MDL-0005).
    '''
    if decision.get("result") != "PASS":
        consequence = {
            "action": "BLOCK",
            "owner": "MetaBlooms",
            "mdl": "MDL-0001",
            "reason_code": decision.get("reason_code") or "DECISION_FAILED"
        }
        raise PromotionBlocked(consequence)
    return {"action": "ALLOW", "owner": "MetaBlooms", "mdl": "MDL-0001"}

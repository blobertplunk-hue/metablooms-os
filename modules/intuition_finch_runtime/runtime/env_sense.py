# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

def sense_environment():
    # v0 minimal: leave adaptive inference for later; return stable keys
    return {
        "stakes": "unknown",
        "verifiability": "unknown",
        "artifact_type": "unknown",
        "audit_required": True,
        "creativity_tolerance": 0.5,
        "latency_budget": "normal"
    }

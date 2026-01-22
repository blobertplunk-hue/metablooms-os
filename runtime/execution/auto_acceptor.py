# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Auto Acceptor
Automatically accepts low-risk auto-patch suggestions and records them to ledger.
"""

from runtime.execution.auto_patch_suggester import suggest_patch

CONFIDENCE_THRESHOLD = 0.8

def auto_accept(pipeline_definition: dict):
    confidence = pipeline_definition.get("confidence", 0.0)
    if confidence < CONFIDENCE_THRESHOLD:
        patch = suggest_patch(pipeline_definition)
        return {
            "accepted": True,
            "patch": patch,
            "confidence": confidence,
            "reason": "Below confidence threshold; auto-accepted"
        }
    return {
        "accepted": False,
        "confidence": confidence,
        "reason": "Confidence above threshold; manual approval required"
    }

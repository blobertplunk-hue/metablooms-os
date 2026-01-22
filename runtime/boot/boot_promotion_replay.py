# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Boot Hook: Promotion Replay
Invoked during boot to reapply registry promotions.
"""

from runtime.execution.promotion_replayer import replay

def on_boot():
    return replay()

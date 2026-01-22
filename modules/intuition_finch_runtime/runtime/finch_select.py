# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import random

FINCHES = ["explorer", "builder", "auditor"]

def select_finch(env: dict):
    # v0: probabilistic, non-deterministic selection with light variance
    # (keeps system adaptive; no scoring yet)
    return {
        "primary_finch": random.choice(FINCHES),
        "selection_strategy": "probabilistic_uniform_v0",
        "exploration_rate": 0.2,
        "random_seed": None
    }

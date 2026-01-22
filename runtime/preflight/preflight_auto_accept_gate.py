# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Preflight Auto-Accept Gate (purified)

Contract alignment:
- NO ledger writes
- NO registry promotion
- Pure decision output only

Returns a legacy-shaped dict that the orchestrator normalizes.
"""

from runtime.execution.auto_acceptor import auto_accept


def preflight(pipeline_definition: dict):
    # Pure decision: auto_acceptor performs analysis and proposes patch/acceptance.
    # Side-effects (ledger, promotion) are owned by orchestrator/execution layers.
    return auto_accept(pipeline_definition)

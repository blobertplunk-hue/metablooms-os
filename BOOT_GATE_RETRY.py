# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_RETRY.py
from retry_policy import with_retry

def gate():
    assert with_retry is not None, "Retry policy missing"
    return True

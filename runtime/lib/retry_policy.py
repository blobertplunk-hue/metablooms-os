# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# runtime/lib/retry_policy.py

import time, random

class RetryForbidden(Exception):
    pass

def with_retry(fn, *, classify, corrective_action, max_attempts=3, base_delay=0.5, ledger=None):
    if not corrective_action:
        raise RetryForbidden("Retry requires corrective_action")
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except Exception as e:
            cls = classify(e)
            if cls == "FORBIDDEN":
                raise
            delay = base_delay * (2 ** (attempt - 1)) + random.random()
            if ledger:
                ledger.log_retry(attempt, cls, corrective_action, delay, str(e))
            time.sleep(delay)
    raise RuntimeError("Retry budget exhausted")

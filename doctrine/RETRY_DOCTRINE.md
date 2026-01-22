# RETRY_DOCTRINE.md

## Purpose
Retries are permitted **only** when they advance system truth. Retrying without transformation is forbidden.

## Core Invariants
1. No retry without an explicit corrective action.
2. All retries must be idempotent or guarded by idempotency keys.
3. All retries must be ledgered.
4. Fail-closed is always preferred over silent success.

## Retry Classes
### Class A — Transient
Retry allowed after bounded backoff.
Examples: network timeout, 5xx, 429.

### Class B — Diagnosable
Retry allowed only after state correction.
Examples: partial extraction, quota exhaustion after wait, temp file collision.

### Class C — Forbidden
Retry not allowed.
Examples: auth failure, SSRF violation, schema violation, missing required artifact.

## Required Fields Per Retry Attempt
- operation_id
- retry_class
- corrective_action
- attempt_number
- delay_ms
- outcome

## Escalation
Auto → Supervisor → Teacher → Human

# CLIP 5 — Reminder Escalation & Decay (P0)

## Problem
Reminders exist but have no urgency model. Important work fades; low-priority work nags.

## Fix
Introduce a Reminder Policy with severity, escalation, snooze, and decay.

### Reminder Policy (schema)
```yaml
reminder:
  thread_id: <string>
  severity: <LOW|MEDIUM|HIGH|CRITICAL>
  cadence: <daily|weekly|monthly>
  escalation:
    after_missed: <int>        # number of misses before escalation
    escalate_to: <severity>
  decay:
    after_days: <int>          # reduce severity if inactive
  snooze:
    allowed: <true|false>
    max_days: <int>
  surfaces:
    - BOOT
    - SHIP
    - REVIEW
```

## Rules (P0)
- CRITICAL reminders surface on BOOT.
- Escalation cannot exceed CRITICAL.
- Snoozed reminders must re-surface after max_days.

## Outcome
- Fewer forgotten priorities
- Less cognitive load
- Trustworthy reminders

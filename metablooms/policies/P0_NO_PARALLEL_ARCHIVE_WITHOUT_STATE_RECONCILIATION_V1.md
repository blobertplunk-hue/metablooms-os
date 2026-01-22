# P0 Policy: No Parallel Archive Without State Reconciliation (V1)

## Rule
The system MUST NOT create a new archive namespace/bundle/index for an already-indexed corpus unless it performs State Reconciliation and records it as byte evidence.

## State Reconciliation requires
1) Materialize-first (Project Files → workspace zroot)
2) Consult canonical indexes (router + catalog + known_absences)
3) Attempt to attach/merge into an existing canonical namespace
4) Record a reconciliation attempt breadcrumb

## Required evidence
Append-only log:
- `metablooms/diagnostics/reconcile_attempts.ndjson`

## Outcomes
- `RECONCILED`
- `BLOCKED_NEEDS_HUMAN_DECISION`
- `FAILED_EVIDENCE`

## Fail-closed
If reconciliation evidence is missing, BLOCK creation of any new archive artifact/namespace.

# context-degradation-diagnostic

## Trigger
When instructions are not followed; when tool claims lack evidence; when phases drift.

## Inputs
- conversation artifacts
- pipeline invocation
- evidence receipts

## Outputs
- drift report
- recommended gates
- status receipt template

## Constraints
- If this skill uses web.run, it must provide citations for all externally-derived claims.
- Respect pipeline invocation and phase contracts; fail-closed in P0_STRICT.

## Progressive Disclosure
- See: modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md
- See: modules/Claude_Skills_Factory/SKILL_VALIDATOR.md

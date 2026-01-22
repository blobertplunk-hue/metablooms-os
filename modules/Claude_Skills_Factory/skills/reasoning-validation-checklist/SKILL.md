# reasoning-validation-checklist

## Trigger
Before recommendations; before shipping; before promoting decisions.

## Inputs
- claims
- evidence table
- phase state

## Outputs
- pass/fail checklist
- missing evidence list

## Constraints
- If this skill uses web.run, it must provide citations for all externally-derived claims.
- Respect pipeline invocation and phase contracts; fail-closed in P0_STRICT.

## Progressive Disclosure
- See: modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md
- See: modules/Claude_Skills_Factory/SKILL_VALIDATOR.md

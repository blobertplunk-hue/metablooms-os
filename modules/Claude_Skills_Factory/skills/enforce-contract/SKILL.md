# enforce-contract

## Trigger
Before writing unit tests; before commit; after AI-generated code; when implementing a spec.

## Inputs
- source files / diffs
- method signatures
- spec frame (optional)

## Outputs
- contract annotations
- assertion stubs
- contract violation report

## Constraints
- If this skill uses web.run, it must provide citations for all externally-derived claims.
- Respect pipeline invocation and phase contracts; fail-closed in P0_STRICT.

## Progressive Disclosure
- See: modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md
- See: modules/Claude_Skills_Factory/SKILL_VALIDATOR.md

# web-automation-executor

## Trigger
When Sandcrawler is invoked or web research is required.

## Inputs
- query plan
- recency requirements
- domains constraints

## Outputs
- sources with citations
- evidence table
- disconfirming pass

## Constraints
- If this skill uses web.run, it must provide citations for all externally-derived claims.
- Respect pipeline invocation and phase contracts; fail-closed in P0_STRICT.

## Progressive Disclosure
- See: modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md
- See: modules/Claude_Skills_Factory/SKILL_VALIDATOR.md

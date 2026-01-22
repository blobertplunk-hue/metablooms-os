# Extraordinary Coding — Clarity Layer (ECL) v1
Contract ID: EXCODE_ECL_V1
Date: 2026-01-16

## Purpose
Make all MetaBlooms code idiot-proof to readers (human or LLM) by enforcing a uniform, machine-checkable “reader contract” for every module.

## Non-negotiable Rule
If a reasonable reader can misinterpret what code does, the code is non-compliant.

## Required File Header (must appear at top of every .py file)
The first non-shebang lines must include an ECL YAML block:

```yaml
# ECL:
#   id: <UNIQUE_STABLE_ID>
#   role: <entrypoint|orchestrator|gate|validator|adapter|schema|io|tool|library>
#   owns: [<owned responsibilities>]
#   does_not: [<explicit non-goals>]
#   inputs: [<input names + types>]
#   outputs: [<output names + types>]
#   side_effects: [<filesystem|ledger|network|none>]
#   failure_modes: [<named failure modes>]
#   invariants: [<named invariants>]
#   evidence: [<what evidence proves it worked>]
#   last_reviewed: YYYY-MM-DD
```

## Required Doc Sections (must exist in module docstring, in this order)
1. Intent
2. Scope
3. Non-Goals
4. Inputs
5. Outputs
6. Side Effects
7. Failure Modes
8. Invariants
9. Evidence & Observability
10. Examples
11. Maintenance Notes

## No Surprise Rules
- No code execution on import.
- No hidden I/O: any write must be routed through an explicit helper.
- Any mutation must be declared in ECL header side_effects.

## Enforcement
Validator: metablooms/validators/excode_ecl_validate_v1.py
Gate ID: GATE.EXCODE.ECL.V1 (recommended P0 once coverage threshold met)

## Integration Plan (minimal)
1) Add validator + gate.
2) Run in WARN until coverage >= 85% of critical modules.
3) Raise to FAIL for critical runs once threshold reached.

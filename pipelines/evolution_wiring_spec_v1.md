# Evolution Seam Wiring Spec v1 (Methodology Governance)

## Goal
Bind methodology governance signals (failure signatures, loop repeats, tool mismatch) into Evolution Seam selection & fitness,
without allowing Evolution to override P0 invariants or governance.

## Contracts
### Inputs (read-only)
- methodology_signals: {failure_signature, failure_count, strategy_id, reroute_triggered, governance_state}
- available_variants
- constraints (P0/P1)

### Outputs (binding)
- selected_variant_id
- constraints (retry limits, clarification allowed)
- reroute_policy (hard triggers)

## Promotion gate
- Any variant with governance violations is ineligible for promotion.

## Freeze semantics
- On repeated failure loop: freeze exploration; quarantine strategy; arbitration required.

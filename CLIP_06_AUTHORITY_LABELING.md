# CLIP 6 — Output Authority Labeling (P0)

## Problem
Outputs appear equally authoritative regardless of evidence maturity.

## Fix
Bind output authority to pipeline phase + evidence gate status.

### Authority Labels
- EXPLORATORY: discovery only; no validation
- PROVISIONAL: partial validation; not decision-safe
- VALIDATED: evidence thresholds met
- ACTIONABLE: validated + promotion passed

### Rule (P0)
Any output must declare its authority label.
Labels downgrade automatically if evidence gate regresses.

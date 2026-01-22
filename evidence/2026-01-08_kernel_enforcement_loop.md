
# Kernel Enforcement Loop (System-Wide)
Date: 2026-01-08

## Execution Order
1. Load global process rules
2. Validate rule bounds
3. Inject rules into:
   - StagePlanner
   - StageRunner
   - InvariantChecker
4. Execute pipeline stages
5. Collect signals for RIDIE

## Guarantee
All engines inherit identical process behavior.

# MB_P0_ENFORCEMENT_COVERAGE_MATRIX (v1)

## BOOT

Running `BOOT_METABLOOMS.py` calls `RUN_METABLOOMS.run()`.

`RUN_METABLOOMS.run()` loads the preflight gate chain at `metablooms/preflight/preflight_gate_chain_v1.json`, executes gates in order, and stops before the first gate whose `module` begins with `runtime.`.

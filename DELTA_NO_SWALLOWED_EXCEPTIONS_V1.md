Delta: NO_SWALLOWED_EXCEPTIONS_V1
Date: 2026-01-16

Intent
- Add a preflight gate that detects swallowed exceptions and bare except blocks.
- Run in P1 WARN mode to surface violations without blocking boot or ship.

Files Added
- metablooms/validators/mb_validate_no_swallowed_exceptions_v1.py
- metablooms/preflight/gates/mb_gate_no_swallowed_exceptions_v1.py

Files Updated
- metablooms/preflight/preflight_gate_chain_v1.json

Gate Wiring
- Gate ID: GATE.CODE.NO_SWALLOWED_EXCEPTIONS.V1
- Level: P1
- Mode: WARN
- Run context override key: mb_no_swallowed_exceptions_mode

Notes
- This delta is intentionally non-blocking. Promote to FAIL only after reviewing false positives.

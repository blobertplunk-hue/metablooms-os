# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.


# validate_shipping_invariants.py
# P0 invariant: never ship a stub or unverifiable OS

import os

MIN_BYTES = 50000  # hard floor

def validate(shipped_zip_path, expected_files):
    assert os.path.exists(shipped_zip_path), "SHIP_FAIL: artifact missing"
    size = os.path.getsize(shipped_zip_path)
    assert size >= MIN_BYTES, f"SHIP_FAIL: artifact too small ({size} bytes)"
    for f in expected_files:
        assert f in shipped_zip_path, f"SHIP_FAIL: missing expected file {f}"
    return {"status":"OK","bytes":size}

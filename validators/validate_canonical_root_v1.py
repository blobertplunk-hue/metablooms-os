#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Fail-closed validator: P0 canonical root enforcement + build_state authority.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def fail(msg: str) -> None:
    print("FAIL:", msg)
    sys.exit(2)

# 1) canonical root module importable
try:
    from runtime.canonical_root import resolve_canonical_root, assert_within_root, CanonicalRootError
except Exception as e:
    fail(f"import runtime.canonical_root: {e}")

# 2) canonical root resolves
try:
    r = resolve_canonical_root()
except Exception as e:
    fail(f"resolve_canonical_root: {e}")

if str(r) != "/mnt/data/MetaBlooms_OS":
    fail(f"canonical root mismatch: {r}")

# 3) build_state exists and matches schema-required fields
bs_path = ROOT / "build_state.json"
if not bs_path.exists():
    fail("build_state.json missing")

try:
    bs = json.loads(bs_path.read_text(encoding="utf-8"))
except Exception as e:
    fail(f"build_state.json parse: {e}")

for k in ["os_version","canonical_root","applied_deltas","last_mutation_ts","integrity_hash"]:
    if k not in bs:
        fail(f"build_state.json missing field: {k}")

if bs.get("canonical_root") != "/mnt/data/MetaBlooms_OS":
    fail("build_state canonical_root mismatch")

# 4) basic write-guard sanity: root itself allowed; /mnt/data escape blocked
try:
    assert_within_root("build_state.json")
except Exception as e:
    fail(f"assert_within_root self-check: {e}")

try:
    # should fail
    assert_within_root("/etc/passwd")
    fail("write escape check did not fail")
except Exception:
    pass

print("PASS: P0 canonical root + build_state")

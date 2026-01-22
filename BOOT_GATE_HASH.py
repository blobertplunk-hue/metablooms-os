# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_HASH.py
# Fail-closed hash verification for MetaBlooms boot (two-tier scheme, backward compatible).
#
# Calling convention (backward compatible):
#   gate(hashes_path="BOOT_HASHES.json", manifest_path="boot_manifest.json")
#
# Tier 1: boot_manifest.json provides authoritative sha256 for BOOT_HASHES.json (boot_hashes_sha256).
# Tier 2: BOOT_HASHES.json lists sha256 for all protected files (excluding itself).

import hashlib
import json
import os

def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def gate(hashes_path: str = "BOOT_HASHES.json", manifest_path: str = "boot_manifest.json") -> bool:
    if not os.path.exists(manifest_path):
        raise RuntimeError("boot_manifest.json missing (hash authority)")
    if not os.path.exists(hashes_path):
        raise RuntimeError("BOOT_HASHES.json missing")

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    expected_hashes_sha = manifest.get("boot_hashes_sha256")
    if not expected_hashes_sha:
        raise RuntimeError("boot_hashes_sha256 missing in boot_manifest.json")

    actual_hashes_sha = _sha256(hashes_path)
    if actual_hashes_sha != expected_hashes_sha:
        raise RuntimeError("Hash mismatch for BOOT_HASHES.json (manifest authority)")

    with open(hashes_path, "r", encoding="utf-8") as f:
        expected = json.load(f)

    # Hard rule: no self-hash entry (prevents paradox)
    if os.path.basename(hashes_path) in expected:
        raise RuntimeError("BOOT_HASHES.json must not contain a self-hash entry")

    for fname, expected_hash in expected.items():
        if not os.path.exists(fname):
            raise RuntimeError(f"Hash target missing: {fname}")
        actual = _sha256(fname)
        if actual != expected_hash:
            raise RuntimeError(f"Hash mismatch for {fname}")
    return True

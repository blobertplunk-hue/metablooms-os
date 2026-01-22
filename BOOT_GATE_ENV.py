# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_ENV.py
# Environment self-measurement gate (fail-closed optional)

import platform, sys, hashlib, json

def fingerprint():
    data = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
    }
    blob = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest(), data

def gate(expected_path=None):
    current_hash, data = fingerprint()
    if expected_path:
        try:
            with open(expected_path) as f:
                expected = json.load(f)
            if expected.get("env_hash") != current_hash:
                raise RuntimeError("Environment hash mismatch")
        except FileNotFoundError:
            raise RuntimeError("Expected environment hash missing")
    return current_hash, data

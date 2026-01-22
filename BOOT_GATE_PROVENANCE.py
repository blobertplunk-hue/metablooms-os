# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_PROVENANCE.py
def gate(config):
    assert config.get("require_provenance", False), "Provenance enforcement disabled"
    return True

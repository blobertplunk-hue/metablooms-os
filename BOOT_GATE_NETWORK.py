# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_NETWORK.py
def gate(network_policy):
    assert network_policy.get("registered", False), "Network boundary not registered"
    return True

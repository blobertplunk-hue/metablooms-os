# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_SANDBOX.py
def gate(env):
    assert env.get("dual_sandbox", False), "Dual sandbox not enforced"
    return True

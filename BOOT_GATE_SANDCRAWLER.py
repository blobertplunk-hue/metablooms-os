# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_SANDCRAWLER.py
def gate(sandcrawler):
    assert sandcrawler.get("escalation_locked", False), "SandCrawler escalation not locked"
    return True

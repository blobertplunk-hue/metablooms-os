# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Segment Resolver
- Selects best segment by capability + availability + evidence tier
- Applies deterministic fallback chains
"""
import json

def resolve(capability, registry, availability):
    chains = registry.get("sections", {})
    for section in chains.values():
        if capability in section.get("chains", {}):
            for seg in section["chains"][capability]:
                reqs = registry["segment_index"][seg].get("requires", [])
                if all(any(r in a for a in availability["executables"]) or "model" in r for r in reqs):
                    return seg
    return None

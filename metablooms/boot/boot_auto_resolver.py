# ECL_VERSION: 1
# ECL_SCOPE: METABLOOMS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.


import os
import re

def resolve_canonical_os(mount_path="/mnt/data"):
    candidates = []
    for f in os.listdir(mount_path):
        if f.lower().endswith(".zip") and "metablooms_os" in f.lower():
            candidates.append(f)
    if not candidates:
        raise RuntimeError("NO_OS_FOUND")
    candidates.sort(reverse=True)
    return os.path.join(mount_path, candidates[0])

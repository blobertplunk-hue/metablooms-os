# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
from pathlib import Path
from .engine import summarize_open_cycles

def surface_open_cycles(root: Path) -> str:
    # Never fails boot.
    try:
        return summarize_open_cycles(root)
    except Exception:
        return "EXPERIENTIAL_LEARNING: error (non-fatal)"

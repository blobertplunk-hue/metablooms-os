# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
from .persistence import record_cycle, load_cycles, list_open_cycles

__all__ = ["record_cycle", "load_cycles", "list_open_cycles"]

def summarize_open_cycles(root: Path, max_items: int = 10) -> str:
    open_cycles = list_open_cycles(root, limit=max_items)
    if not open_cycles:
        return "EXPERIENTIAL_LEARNING: none"
    lines = [f"EXPERIENTIAL_LEARNING: open_cycles={len(open_cycles)}"]
    for c in open_cycles:
        prompt = (c.get("prompt") or "").strip().replace("\n"," ")
        if len(prompt) > 120:
            prompt = prompt[:117] + "..."
        lines.append(f"- {c.get('cycle_id','el_?')}: {prompt}")
    return "\n".join(lines)

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
from pathlib import Path
from .persistence import load_open_threads

def surface_open_threads(root: Path, max_items: int = 10) -> str:
    """Return a human-readable boot banner. Never fails boot."""
    open_threads = load_open_threads(root, limit=max_items)
    if not open_threads:
        return "HANGING_THREADS: none"
    lines = [f"⚠️ HANGING THREADS PRESENT ({len(open_threads)})"]
    for t in open_threads:
        trig = (t.get("trigger_text") or "").strip().replace("\n", " ")
        if len(trig) > 140:
            trig = trig[:137] + "..."
        lines.append(f"- {t.get('thread_id','ht_?')}: {trig}")
    return "\n".join(lines)

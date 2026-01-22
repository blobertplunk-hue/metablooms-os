# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import hashlib, re, time
from typing import Iterable, Dict, Any, List

DEFAULT_TRIGGERS = [
    "put a pin", "pin this", "come back", "do this later", "later",
    "remind me", "unfinished", "not finished", "needs followup",
    "we should", "next time", "follow up", "next action", "follow-up"
]

def _stable_id(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return "ht_" + h[:12]

def detect_threads(texts: Iterable[str], source: str, triggers: List[str] | None = None) -> List[Dict[str, Any]]:
    """Rule-based detection. Returns thread records (status=open)."""
    triggers = triggers or DEFAULT_TRIGGERS
    out: List[Dict[str, Any]] = []
    for t in texts:
        low = (t or "").lower()
        if any(k in low for k in triggers):
            tid = _stable_id(low.strip()[:500])
            out.append({
                "thread_id": tid,
                "status": "open",
                "trigger_text": t.strip()[:5000],
                "ts_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source": source,
                "evidence": None,
                "references": None
            })
    return out

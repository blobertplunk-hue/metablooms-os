# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
import json, time, hashlib
from pathlib import Path
from typing import Dict, Any, Iterable, List

DATA_REL = Path("data/experiential_learning/cycles.ndjson")

def ensure_store(root: Path) -> Path:
    p = root / DATA_REL
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("", encoding="utf-8")
    return p

def _cycle_id(prompt: str) -> str:
    h = hashlib.sha256((prompt or '').encode('utf-8')).hexdigest()
    return "el_" + h[:12]

def append_cycles(root: Path, records: Iterable[Dict[str, Any]]) -> int:
    p = ensure_store(root)
    n = 0
    with p.open("a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, sort_keys=True) + "\n")
            n += 1
    return n

def load_cycles(root: Path, limit: int = 5000) -> List[Dict[str, Any]]:
    p = ensure_store(root)
    out: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                # fail-closed for engine use; caller decides behavior
                continue
            if len(out) >= limit:
                break
    return out

def list_open_cycles(root: Path, limit: int = 200) -> List[Dict[str, Any]]:
    cycles = load_cycles(root)
    # last-write-wins by cycle_id
    state: Dict[str, Dict[str, Any]] = {}
    for c in cycles:
        cid = c.get("cycle_id")
        if not cid:
            continue
        state[cid] = c
    open_list = [v for v in state.values() if v.get("status") == "open"]
    open_list.sort(key=lambda x: x.get("ts_utc",""))
    return open_list[:limit]

def record_cycle(root: Path, prompt: str, observations=None, hypotheses=None, actions=None, results=None, status: str="open", evidence=None, references=None) -> Dict[str, Any]:
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    rec = {
        "cycle_id": _cycle_id(prompt),
        "status": status,
        "ts_utc": ts,
        "prompt": prompt or "",
        "observations": list(observations or []),
        "hypotheses": list(hypotheses or []),
        "actions": list(actions or []),
        "results": list(results or []),
        "evidence": evidence,
        "references": references
    }
    append_cycles(root, [rec])
    return rec

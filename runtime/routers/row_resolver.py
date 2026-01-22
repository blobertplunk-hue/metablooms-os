# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
ROW Resolver
Authoritative resolver for mapping user intent to canonical ROWs.
"""

import re
import json
from pathlib import Path

MASTER_PATH = Path(__file__).parents[2] / "registry" / "artifact2_rows_pipelines" / "consolidated" / "artifact2_rows_pipelines_master_v1.json"

def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def load_rows():
    data = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
    return data.get("rows", [])

def score_match(prompt: str, row_name: str) -> float:
    p = normalize(prompt)
    r = normalize(row_name)
    if r in p:
        return 0.95
    overlap = set(p.split()) & set(r.split())
    if not overlap:
        return 0.0
    return len(overlap) / max(len(r.split()), 1)

def resolve_row(prompt: str, threshold: float = 0.65):
    rows = load_rows()
    best = {"row": None, "score": 0.0}
    for r in rows:
        s = score_match(prompt, r["name"])
        if s > best["score"]:
            best = {"row": r, "score": s}
    if best["row"] and best["score"] >= threshold:
        return {
            "status": "RESOLVED",
            "row_id": best["row"]["id"],
            "row_name": best["row"]["name"],
            "confidence": round(best["score"], 3),
            "source": "artifact2_master"
        }
    return {
        "status": "UNRESOLVED",
        "confidence": round(best["score"], 3),
        "reason": "No ROW exceeded confidence threshold"
    }

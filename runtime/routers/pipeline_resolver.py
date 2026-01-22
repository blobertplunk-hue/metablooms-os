# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Pipeline Resolver (patched)
Resolves canonical pipelines from a resolved ROW and returns pipeline definitions
including sections (when present in canonical registry).
"""

import re
import json
from pathlib import Path

MASTER_PATH = Path(__file__).parents[2] / "registry" / "artifact2_rows_pipelines" / "consolidated" / "artifact2_rows_pipelines_master_v1.json"

def normalize(text: str) -> str:
    text = (text or "").lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text

def load_master():
    return json.loads(MASTER_PATH.read_text(encoding="utf-8"))

def score_pipeline(row_name: str, pipeline_name: str) -> float:
    r = set(normalize(row_name).split())
    p = set(normalize(pipeline_name).split())
    if not r or not p:
        return 0.0
    overlap = r & p
    return len(overlap) / max(len(r), 1)

def resolve_pipelines(row_resolution: dict, threshold: float = 0.5):
    if row_resolution.get("status") != "RESOLVED":
        return {"status": "BLOCKED", "reason": "ROW_NOT_RESOLVED"}

    row_name = row_resolution.get("row_name")
    data = load_master()
    pipelines = data.get("pipelines", [])

    scored = []
    for p in pipelines:
        s = score_pipeline(row_name, p.get("name", ""))
        if s >= threshold:
            scored.append({
                "pipeline_id": p.get("id"),
                "pipeline_name": p.get("name"),
                "confidence": round(s, 3),
                "source": "artifact2_master",
                # include sections if known (else empty; downstream can infer/patch)
                "sections": p.get("sections", []),
                "sections_source": p.get("sections_source"),
                "sections_confidence": p.get("sections_confidence"),
            })

    if not scored:
        return {"status": "UNRESOLVED", "row_name": row_name, "reason": "No pipeline exceeded confidence threshold"}

    scored.sort(key=lambda x: x["confidence"], reverse=True)
    return {"status": "RESOLVED", "row_name": row_name, "pipelines": scored}

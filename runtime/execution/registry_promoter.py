# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Registry Promoter
Promotes auto-accepted pipe section patches into the canonical pipeline registry.

Fail-closed principles:
- If a pipeline_id cannot be found in the canonical registry, do NOT invent it.
- Always create an append-only promotion record in diagnostics.
- Always write a backup of the registry before mutating it.
"""

import json
from pathlib import Path
from datetime import datetime

MASTER_PATH = Path(__file__).parents[2] / "registry" / "artifact2_rows_pipelines" / "consolidated" / "artifact2_rows_pipelines_master_v1.json"
BACKUP_DIR = Path(__file__).parents[2] / "diagnostics" / "registry_backups"
PROMOTION_LEDGER = Path(__file__).parents[2] / "ledger" / "registry_promotions.jsonl"

def _utc_stamp():
    return datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _read_master():
    return json.loads(MASTER_PATH.read_text(encoding="utf-8"))

def _write_master(data: dict):
    MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MASTER_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")

def _backup_master():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_path = BACKUP_DIR / f"artifact2_rows_pipelines_master_v1.{_utc_stamp()}.bak.json"
    backup_path.write_text(MASTER_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return backup_path

def _append_promotion(entry: dict):
    PROMOTION_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(PROMOTION_LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def promote_sections(pipeline_id: str, suggested_sections: list, confidence: float = None, source: str = "auto_accept"):
    """
    Mutates canonical registry in-place (with backup + promotion ledger).
    """
    if not pipeline_id or not isinstance(suggested_sections, list) or not suggested_sections:
        return {"ok": False, "failure": "INVALID_INPUT"}

    if not MASTER_PATH.exists():
        return {"ok": False, "failure": "MASTER_REGISTRY_MISSING", "path": str(MASTER_PATH)}

    backup = _backup_master()
    data = _read_master()
    pipelines = data.get("pipelines", [])
    hit = None
    for p in pipelines:
        if p.get("id") == pipeline_id:
            hit = p
            break

    if hit is None:
        _append_promotion({
            "ok": False,
            "failure": "PIPELINE_ID_NOT_FOUND",
            "pipeline_id": pipeline_id,
            "suggested_sections": suggested_sections,
            "confidence": confidence,
            "source": source,
            "backup": str(backup)
        })
        # restore not needed (no mutation)
        return {"ok": False, "failure": "PIPELINE_ID_NOT_FOUND", "pipeline_id": pipeline_id}

    # apply promotion
    hit["sections"] = suggested_sections
    hit["sections_source"] = source
    if confidence is not None:
        hit["sections_confidence"] = confidence

    _write_master(data)

    _append_promotion({
        "ok": True,
        "pipeline_id": pipeline_id,
        "suggested_sections": suggested_sections,
        "confidence": confidence,
        "source": source,
        "backup": str(backup)
    })

    return {"ok": True, "pipeline_id": pipeline_id, "backup": str(backup)}

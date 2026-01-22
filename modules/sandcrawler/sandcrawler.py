# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
MetaBlooms Sandcrawler Module (Minimal)

Design intent:
- In-chat, Sandcrawler corresponds to external evidence gathering (e.g., web.run).
- This runtime cannot execute web queries by itself; instead it produces *job files*
  that a supervising environment (a chat/tool runner) can execute and then attach
  results back into the OS evidence ledger.

Fail-closed posture:
- The module never fabricates evidence. It only queues jobs and records expected outputs.
"""

from __future__ import annotations

import json
import hashlib


def _sha256_job(job_id: str) -> str:
    """Deterministic SHA256 for a job id."""
    import hashlib
    return hashlib.sha256(job_id.encode('utf-8')).hexdigest()
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
from typing import List, Optional, Dict, Any

ROOT = Path(__file__).resolve().parents[2]  # OS root
JOBS_DIR = ROOT / "sandcrawler_jobs"
OUT_DIR = ROOT / "sandcrawler_outputs"
STATE_DIR = ROOT / "sandcrawler_state"

@dataclass
class SandcrawlerJob:
    job_id: str
    created_utc: str
    purpose: str
    queries: List[str]
    qdf: Optional[int] = None
    domains: Optional[List[str]] = None
    notes: Optional[str] = None
    expected_artifacts: Optional[List[str]] = None
    status: str = "QUEUED"  # QUEUED | RUNNING | COMPLETE | FAILED

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

def activate() -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "SANDCRAWLER_READY.json").write_text(json.dumps({
        "ready": True,
        "created_utc": _utc_now(),
        "module": "sandcrawler",
        "mode": "queue-only",
        "note": "This module queues Sandcrawler jobs; an external runner must execute them."
    }, indent=2), encoding="utf-8")

def queue_job(
    *,
    purpose: str,
    queries: List[str],
    qdf: Optional[int] = None,
    domains: Optional[List[str]] = None,
    notes: Optional[str] = None,
    expected_artifacts: Optional[List[str]] = None
) -> Path:
    if not purpose or not isinstance(purpose, str):
        raise ValueError("purpose must be a non-empty string")
    if not queries or not all(isinstance(q, str) and q.strip() for q in queries):
        raise ValueError("queries must be a non-empty list of non-empty strings")

    job = SandcrawlerJob(
        job_id=str(uuid4()),
        created_utc=_utc_now(),
        purpose=purpose.strip(),
        queries=[q.strip() for q in queries],
        qdf=qdf,
        domains=domains,
        notes=notes,
        expected_artifacts=expected_artifacts,
    )
    path = JOBS_DIR / f"{job.job_id}.job.json"
    path.write_text(json.dumps(asdict(job), indent=2), encoding="utf-8")
    return path

def record_result(job_id: str, result: Dict[str, Any]) -> Path:
    """Store the runner's result payload next to the job."""
    if not job_id:
        raise ValueError("job_id required")
    out_path = OUT_DIR / f"{job_id}.result.json"
    out_path.write_text(json.dumps({
        "job_id": job_id,
        "recorded_utc": _utc_now(),
        "job_sha256": _sha256_job(job_id),
        "result": result
    }, indent=2), encoding="utf-8")
    return out_path

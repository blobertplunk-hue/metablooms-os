# ECL_VERSION: 1
# ECL_SCOPE: METABLOOMS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""Post-Run Hook v1

Purpose
-------
Provide a single callable that the run lifecycle may invoke after preflight
completes. The hook must be:

- deterministic
- side-effect limited to writing post-run artifacts
- safe to call on both success and failure paths

Outputs (stable paths)
----------------------
- metablooms/postrun/prr_report_v1.json
- metablooms/postrun/mmts/*.json
- ledger/evidence_log_v2.md (append-only)

Run-specific outputs are also written under:
- metablooms/postrun/_runs/<run_id>/
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from metablooms.postrun.prr_runner_v1 import write_outputs


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root() -> Path:
    # metablooms/postrun/postrun_hook_v1.py -> metablooms/postrun -> metablooms -> <root>
    return Path(__file__).resolve().parents[2]


def _ensure_minimal_evidence(evidence_path: Path, run_id: str, preflight_ok: bool) -> None:
    """Create a minimal evidence log when none is provided.

    This prevents the PRR runner from failing due to missing input, while still
    avoiding invention of evidence.
    """

    if evidence_path.exists():
        return

    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    content = [
        "# Auto Evidence (Generated)",
        "",
        f"run_id: {run_id}",
        f"created_utc: {_utc_now()}",
        f"preflight_ok: {preflight_ok}",
        "",
        "NOTE: No evidence_log_path was provided in run_context.",
        "This file is a minimal placeholder to allow PRR to run.",
    ]
    evidence_path.write_text("\n".join(content) + "\n", encoding="utf-8")


def _split_mmts(mmt_queue_path: Path, mmts_dir: Path) -> None:
    mmts_dir.mkdir(parents=True, exist_ok=True)
    try:
        data = json.loads(mmt_queue_path.read_text(encoding="utf-8"))
    except Exception:
        return
    tickets = data.get("tickets", []) if isinstance(data, dict) else []
    for t in tickets:
        mmt_id = t.get("mmt_id", "MMT_UNKNOWN")
        (mmts_dir / f"{mmt_id}.json").write_text(json.dumps(t, indent=2), encoding="utf-8")


def _append_evidence_log(evidence_log_v2_path: Path, entry: Dict[str, Any]) -> None:
    evidence_log_v2_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "\n---\n",
        f"created_utc: {entry.get('created_utc','')}",
        f"artifact_path: {entry.get('artifact_path','')}",
        f"sweep_id: {entry.get('sweep_id','')}",
        f"evidence_weight: {entry.get('evidence_weight','')}",
        f"failure_signal: {entry.get('failure_signal','')}",
        f"owner: {entry.get('owner','')}",
        f"next_review_date: {entry.get('next_review_date','')}",
        "",
    ]
    evidence_log_v2_path.write_text(
        (evidence_log_v2_path.read_text(encoding="utf-8") if evidence_log_v2_path.exists() else "")
        + "\n".join(lines),
        encoding="utf-8",
    )


def run_postrun_review(*, run_context: Dict[str, Any], preflight_result: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke PRR v1 and return a summary dict.

    This function must never raise in normal operation; errors are returned as
    structured violations in the summary.
    """

    root = _repo_root()
    postrun_dir = root / "metablooms" / "postrun"
    ledger_dir = root / "ledger"

    run_id = str(run_context.get("run_id") or f"run_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
    evidence_log_path_str = run_context.get("evidence_log_path") or ""
    evidence_path = Path(evidence_log_path_str) if evidence_log_path_str else (postrun_dir / f"_auto_evidence_{run_id}.md")

    _ensure_minimal_evidence(evidence_path, run_id, bool(preflight_result.get("ok")))

    # Ensure ledger exists (even if empty) so downstream tools have a stable path.
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_ndjson = ledger_dir / "ledger.ndjson"
    if not ledger_ndjson.exists():
        ledger_ndjson.write_text("", encoding="utf-8")

    run_out_dir = postrun_dir / "_runs" / run_id
    try:
        write_outputs(
            out_dir=run_out_dir,
            run_id=run_id,
            evidence_log_path=str(evidence_path),
            ledger_path=str(ledger_ndjson),
            diff_manifest_path=str(run_context.get("diff_manifest_path") or ""),
        )
    except Exception as e:
        return {
            "ok": False,
            "run_id": run_id,
            "error": f"PRR_FAILED: {e.__class__.__name__}: {e}",
        }

    # Promote latest outputs to stable paths
    latest_report = run_out_dir / "prr_report_v1.json"
    latest_mmt_queue = run_out_dir / "mmt_queue_v1.json"
    latest_summary = run_out_dir / "prr_summary_v1.md"

    if latest_report.exists():
        (postrun_dir / "prr_report_v1.json").write_text(latest_report.read_text(encoding="utf-8"), encoding="utf-8")
    if latest_summary.exists():
        (postrun_dir / "prr_summary_v1.md").write_text(latest_summary.read_text(encoding="utf-8"), encoding="utf-8")

    mmts_dir = postrun_dir / "mmts"
    if latest_mmt_queue.exists():
        _split_mmts(latest_mmt_queue, mmts_dir)

    # Append evidence log v2 entry
    evidence_log_v2 = ledger_dir / "evidence_log_v2.md"
    _append_evidence_log(
        evidence_log_v2,
        {
            "created_utc": _utc_now(),
            "artifact_path": str(postrun_dir / "prr_report_v1.json"),
            "sweep_id": f"PRR_V1_{run_id}",
            "evidence_weight": "MED",
            "failure_signal": "" if preflight_result.get("ok") else "PREFLIGHT_FAIL",
            "owner": "metablooms.postrun",
            "next_review_date": "",
        },
    )

    return {
        "ok": True,
        "run_id": run_id,
        "prr_report": str(postrun_dir / "prr_report_v1.json"),
        "mmts_dir": str(mmts_dir),
    }

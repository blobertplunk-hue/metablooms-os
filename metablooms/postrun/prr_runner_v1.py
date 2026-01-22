# ECL_VERSION: 1
# ECL_SCOPE: METABLOOMS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Post-Run Review (PRR) Runner v1

Design goals:
- deterministic ticket IDs
- no invention of evidence
- outputs: prr_report_v1.json, mmt_queue_v1.json, prr_summary_v1.md

This runner is intentionally conservative: it detects common failure/friction signals
from an Evidence Log and optional ledger.ndjson and emits MMTs.

NOTE: This file is shipped as a runnable module, but execution wiring is separate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SIGNAL_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    ("DOWNLOAD_LINK_FAILURE", re.compile(r"error downloading|expired|download.*fail", re.IGNORECASE)),
    ("TRUNCATION_RISK", re.compile(r"truncat|ellips", re.IGNORECASE)),
    ("AMBIGUITY_LOOP", re.compile(r"ambig|guess|fail-closed", re.IGNORECASE)),
    ("MISSING_AUTHORITY", re.compile(r"authority boundary|no single|not authoritative", re.IGNORECASE)),
    ("UNVERIFIED_EXECUTION_CLAIM", re.compile(r"boot_ok|executed|ran", re.IGNORECASE)),
]


def _sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8"), usedforsecurity=False).hexdigest()


def _stable_id(prefix: str, *parts: str) -> str:
    h = _sha1("|".join(parts))[:10]
    return f"{prefix}_{h}"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def detect_signals(evidence_text: str) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    for sig, pat in SIGNAL_PATTERNS:
        if pat.search(evidence_text):
            fid = _stable_id("finding", sig, evidence_text[:500])
            findings.append(
                {
                    "finding_id": fid,
                    "type": sig,
                    "summary": f"Detected signal: {sig}",
                    "severity": "MED" if sig not in {"UNVERIFIED_EXECUTION_CLAIM"} else "HIGH",
                    "evidence_refs": ["EvidenceLog:pattern:" + sig],
                    "inference": False,
                }
            )
    return findings


def propose_mmts(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    tickets: List[Dict[str, Any]] = []
    for f in findings:
        sig = f["type"]
        if sig == "DOWNLOAD_LINK_FAILURE":
            tickets.append(
                {
                    "mmt_id": _stable_id("MMT", "DL-REGEN", f["finding_id"]),
                    "phase": "Ship",
                    "problem": "Download links can fail/expire in client.",
                    "proposal": "Always publish a 'regen-on-failure' ship step: repackage artifacts under fresh filenames and ship 3-tuple (zip, sha256, evidence log).",
                    "expected_gain": "Fewer blocked users; deterministic recovery.",
                    "risk": "Low (packaging only).",
                    "status": "Proposed",
                    "evidence_refs": f["evidence_refs"],
                }
            )
        elif sig == "TRUNCATION_RISK":
            tickets.append(
                {
                    "mmt_id": _stable_id("MMT", "FILE-FIRST", f["finding_id"]),
                    "phase": "Build",
                    "problem": "Inline code outputs are prone to truncation.",
                    "proposal": "Enforce file-first for OS mutations; forbid inline code in governed runs.",
                    "expected_gain": "Higher integrity artifacts; less rework.",
                    "risk": "Low.",
                    "status": "Proposed",
                    "evidence_refs": f["evidence_refs"],
                }
            )
        elif sig == "AMBIGUITY_LOOP":
            tickets.append(
                {
                    "mmt_id": _stable_id("MMT", "FAIL-TO-FIX", f["finding_id"]),
                    "phase": "Gate",
                    "problem": "Repeated fail-closed loops on authorable primitives.",
                    "proposal": "Adopt 'fail-to-fix' rule: if a required primitive can be authored deterministically, author it and continue; fail-closed only on unknown ambiguity.",
                    "expected_gain": "Faster progress; fewer turns.",
                    "risk": "Medium (requires clear bounds).",
                    "status": "Proposed",
                    "evidence_refs": f["evidence_refs"],
                }
            )
        elif sig == "MISSING_AUTHORITY":
            tickets.append(
                {
                    "mmt_id": _stable_id("MMT", "AUTH-DECL", f["finding_id"]),
                    "phase": "Design",
                    "problem": "Authority boundaries are implicit, causing wiring ambiguity.",
                    "proposal": "Require explicit authority declarations (entrypoint json) for orchestrators and gates.",
                    "expected_gain": "Less ambiguity; safer wiring.",
                    "risk": "Low.",
                    "status": "Proposed",
                    "evidence_refs": f["evidence_refs"],
                }
            )
    return tickets


def write_outputs(out_dir: Path, run_id: str, evidence_log_path: str, ledger_path: Optional[str] = None, diff_manifest_path: Optional[str] = None) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    evidence_text = _read_text(Path(evidence_log_path))
    findings = detect_signals(evidence_text)
    tickets = propose_mmts(findings)

    mmt_queue = {"version": 1, "tickets": tickets}
    mmt_path = out_dir / "mmt_queue_v1.json"
    mmt_path.write_text(json.dumps(mmt_queue, indent=2), encoding="utf-8")

    report = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "evidence_log_path": evidence_log_path,
            "ledger_path": ledger_path or "",
            "diff_manifest_path": diff_manifest_path or "",
        },
        "findings": findings,
        "mmt_queue_path": str(mmt_path),
    }
    (out_dir / "prr_report_v1.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # lightweight human summary
    summary_lines = [
        "# PRR Summary (v1)",
        "",
        f"## Run\n- Run ID: {run_id}",
        "",
        "## Top findings",
    ]
    if not findings:
        summary_lines.append("- None detected")
    else:
        for f in findings[:5]:
            summary_lines.append(f"- {f['type']}: {f['summary']}")

    summary_lines.append("\n## MMTs proposed")
    if not tickets:
        summary_lines.append("- None")
    else:
        for t in tickets[:10]:
            summary_lines.append(f"- {t['mmt_id']} ({t['phase']}): {t['proposal']}")

    (out_dir / "prr_summary_v1.md").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--evidence-log", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--diff", default=None)
    args = ap.parse_args()

    write_outputs(Path(args.out_dir), args.run_id, args.evidence_log, args.ledger, args.diff)

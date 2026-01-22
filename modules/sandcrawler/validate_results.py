# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
MetaBlooms Sandcrawler Result Validator (offline)

Purpose:
- Validate *structure*, *integrity*, and *traceability* of Sandcrawler outputs without internet access.
- This does NOT validate factual correctness of sources; it validates that outputs are:
  (a) present, (b) parseable, (c) internally consistent, (d) traceable to queued jobs.

Inputs (default):
- modules/sandcrawler/out/
  - *.job.json        (queued jobs)
  - *.result.json     (results produced by an external runner)

Outputs:
- modules/sandcrawler/out/sandcrawler_validation_report.json
- modules/sandcrawler/out/sandcrawler_validation_report.md

Strictness:
- Non-strict: missing results are WARN (useful when queueing jobs for later execution).
- Strict: missing results are FAIL.

Configuration:
- Pass strict=True/False to validate_sandcrawler_outputs()
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ISO_Z_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _utc_now_z() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_bytes(b: bytes) -> str:
    return sha256(b).hexdigest()


def _read_json(path: Path) -> Tuple[Optional[dict], Optional[str]]:
    try:
        raw = path.read_bytes()
    except Exception as e:
        return None, f"READ_ERROR: {e}"
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as e:
        return None, f"JSON_ERROR: {e}"
    if not isinstance(obj, dict):
        return None, "TYPE_ERROR: root is not an object"
    return obj, None


@dataclass
class Finding:
    severity: str  # "FAIL" | "WARN" | "INFO"
    code: str
    message: str
    path: Optional[str] = None
    job_id: Optional[str] = None


@dataclass
class ValidationReport:
    schema_version: str
    generated_utc: str
    strict: bool
    out_dir: str
    jobs_found: int
    results_found: int
    matched_pairs: int
    failures: int
    warnings: int
    infos: int
    findings: List[Finding]


def validate_sandcrawler_outputs(out_dir: Path, strict: bool = False) -> ValidationReport:
    findings: List[Finding] = []

    if not out_dir.exists():
        findings.append(Finding("FAIL" if strict else "WARN", "OUT_DIR_MISSING",
                                f"Sandcrawler out_dir not found: {out_dir}", path=str(out_dir)))
        rep = ValidationReport(
            schema_version="SCVAL-1",
            generated_utc=_utc_now_z(),
            strict=strict,
            out_dir=str(out_dir),
            jobs_found=0,
            results_found=0,
            matched_pairs=0,
            failures=sum(1 for f in findings if f.severity == "FAIL"),
            warnings=sum(1 for f in findings if f.severity == "WARN"),
            infos=sum(1 for f in findings if f.severity == "INFO"),
            findings=findings,
        )
        return rep

    job_files = sorted(out_dir.glob("*.job.json"))
    result_files = sorted(out_dir.glob("*.result.json"))

    jobs: Dict[str, Path] = {}
    results: Dict[str, Path] = {}

    for p in job_files:
        # expected pattern: <job_id>.job.json
        job_id = p.name.replace(".job.json", "")
        jobs[job_id] = p

    for p in result_files:
        job_id = p.name.replace(".result.json", "")
        results[job_id] = p

    if not jobs:
        findings.append(Finding("WARN", "NO_JOBS", "No Sandcrawler job files found.", path=str(out_dir)))

    matched = 0

    for job_id, job_path in jobs.items():
        job_obj, err = _read_json(job_path)
        if err:
            findings.append(Finding("FAIL", "JOB_INVALID_JSON", f"{err}", path=str(job_path), job_id=job_id))
            continue

        # Minimal job checks
        if job_obj.get("job_id") != job_id:
            findings.append(Finding("FAIL", "JOB_ID_MISMATCH",
                                    f"job_id in file does not match filename ({job_obj.get('job_id')} != {job_id})",
                                    path=str(job_path), job_id=job_id))

        created_utc = job_obj.get("created_utc")
        if not (isinstance(created_utc, str) and ISO_Z_RE.match(created_utc)):
            findings.append(Finding("WARN", "JOB_CREATED_UTC_FORMAT",
                                    f"created_utc missing or not Z-ISO8601: {created_utc}",
                                    path=str(job_path), job_id=job_id))

        query = job_obj.get("query")
        if not isinstance(query, str) or not query.strip():
            findings.append(Finding("FAIL", "JOB_QUERY_EMPTY", "Job query missing/empty.", path=str(job_path), job_id=job_id))

        # Result presence
        res_path = results.get(job_id)
        if not res_path:
            findings.append(Finding("FAIL" if strict else "WARN", "RESULT_MISSING",
                                    "No result file found for job.", path=str(job_path), job_id=job_id))
            continue

        matched += 1
        res_obj, rerr = _read_json(res_path)
        if rerr:
            findings.append(Finding("FAIL", "RESULT_INVALID_JSON", f"{rerr}", path=str(res_path), job_id=job_id))
            continue

        if res_obj.get("job_id") != job_id:
            findings.append(Finding("FAIL", "RESULT_JOB_ID_MISMATCH",
                                    f"job_id in result does not match filename ({res_obj.get('job_id')} != {job_id})",
                                    path=str(res_path), job_id=job_id))

        recorded_utc = res_obj.get("recorded_utc")
        if not (isinstance(recorded_utc, str) and ISO_Z_RE.match(recorded_utc)):
            findings.append(Finding("WARN", "RESULT_RECORDED_UTC_FORMAT",
                                    f"recorded_utc missing or not Z-ISO8601: {recorded_utc}",
                                    path=str(res_path), job_id=job_id))

        # Traceability / integrity: embed hash of job file in result if present
        job_hash = _sha256_bytes(job_path.read_bytes())
        res_job_hash = res_obj.get("job_sha256")
        if res_job_hash is None:
            findings.append(Finding("INFO", "RESULT_NO_JOB_HASH",
                                    "Result does not include job_sha256; recommend adding for tamper detection.",
                                    path=str(res_path), job_id=job_id))
        elif res_job_hash != job_hash:
            findings.append(Finding("FAIL", "RESULT_JOB_HASH_MISMATCH",
                                    "Result job_sha256 does not match current job file content.",
                                    path=str(res_path), job_id=job_id))

        # Evidence minimalism: require at least one source entry if job claims it's a research run
        sources = res_obj.get("sources")
        if sources is None and isinstance(res_obj.get("result"), dict):
            sources = res_obj["result"].get("sources")
        if sources is None:
            findings.append(Finding("WARN", "RESULT_NO_SOURCES",
                                    "Result has no 'sources' field; cannot verify traceability to evidence.",
                                    path=str(res_path), job_id=job_id))
        elif not isinstance(sources, list):
            findings.append(Finding("FAIL", "RESULT_SOURCES_TYPE",
                                    "Result 'sources' must be a list.", path=str(res_path), job_id=job_id))
        else:
            if len(sources) == 0:
                findings.append(Finding("FAIL" if strict else "WARN", "RESULT_SOURCES_EMPTY",
                                        "Result has an empty sources list.", path=str(res_path), job_id=job_id))
            # light schema check per source
            for i, s in enumerate(sources[:50]):  # cap to avoid huge logs
                if not isinstance(s, dict):
                    findings.append(Finding("FAIL", "SOURCE_NOT_OBJECT",
                                            f"Source[{i}] is not an object.", path=str(res_path), job_id=job_id))
                    continue
                # allow either ref_id or url; at least one must exist
                if not (isinstance(s.get("ref_id"), str) and s.get("ref_id")) and not (isinstance(s.get("url"), str) and s.get("url")):
                    findings.append(Finding("WARN", "SOURCE_MISSING_ID",
                                            f"Source[{i}] lacks ref_id/url.", path=str(res_path), job_id=job_id))

    # Orphan results
    for job_id, res_path in results.items():
        if job_id not in jobs:
            findings.append(Finding("WARN", "ORPHAN_RESULT",
                                    "Result exists without corresponding job file.", path=str(res_path), job_id=job_id))

    failures = sum(1 for f in findings if f.severity == "FAIL")
    warnings = sum(1 for f in findings if f.severity == "WARN")
    infos = sum(1 for f in findings if f.severity == "INFO")

    return ValidationReport(
        schema_version="SCVAL-1",
        generated_utc=_utc_now_z(),
        strict=strict,
        out_dir=str(out_dir),
        jobs_found=len(job_files),
        results_found=len(result_files),
        matched_pairs=matched,
        failures=failures,
        warnings=warnings,
        infos=infos,
        findings=findings,
    )


def write_report(out_dir: Path, report: ValidationReport) -> Tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "sandcrawler_validation_report.json"
    md_path = out_dir / "sandcrawler_validation_report.md"

    json_path.write_text(json.dumps({
        **asdict(report),
        "findings": [asdict(f) for f in report.findings],
    }, indent=2), encoding="utf-8")

    # Markdown summary
    lines = []
    lines.append(f"# Sandcrawler Validation Report ({report.schema_version})")
    lines.append("")
    lines.append(f"- Generated (UTC): {report.generated_utc}")
    lines.append(f"- Strict mode: {report.strict}")
    lines.append(f"- Out dir: `{report.out_dir}`")
    lines.append(f"- Jobs found: {report.jobs_found}")
    lines.append(f"- Results found: {report.results_found}")
    lines.append(f"- Matched pairs: {report.matched_pairs}")
    lines.append(f"- Failures: {report.failures}")
    lines.append(f"- Warnings: {report.warnings}")
    lines.append(f"- Infos: {report.infos}")
    lines.append("")
    if not report.findings:
        lines.append("No findings.")
    else:
        lines.append("## Findings")
        for f in report.findings:
            loc = f" ({f.path})" if f.path else ""
            jid = f"[{f.job_id}] " if f.job_id else ""
            lines.append(f"- **{f.severity}** {jid}{f.code}: {f.message}{loc}")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    return json_path, md_path

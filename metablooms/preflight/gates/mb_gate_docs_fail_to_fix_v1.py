# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: DOCS.FAIL_TO_FIX (v1)

P0 preflight gate.

Purpose
- Enforce documentation invariants for LLM-safe system self-description.
- Implement FAIL-TO-FIX for forbidden terms:
  - Class A: quarantine clearly historical notes out of the boot-scanned docs surface.
  - Class B: deterministic, ontology-approved rewrite for non-canonical docs.

Safety
- Never edits CANONICAL_ONTOLOGY.md or ARCHITECTURE_LITERAL.md.
- Never allowlists forbidden terms.
- Repairs are logged to ledgers/auto_repairs.jsonl.

Failure model
- If violations remain after safe repair attempts, gate fails closed.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

GATE_ID = "GATE.P0.DOCS.FAIL_TO_FIX.V1"
P0 = True

# If the ontology file cannot be parsed, we fail closed.
DEFAULT_FORBIDDEN = [
    "Kernel",
    "Cognitive Stack",
    "Governance Stack",
    "Supervisor",
    "Self-governing",
    "Autonomous",
    "Meta-cognition",
]

# Deterministic Class-B rewrites (exact string replacement, case-sensitive)
CLASS_B_REWRITE = {
    "Kernel": "runtime core",
}

HISTORICAL_NAME_HINTS = ("note", "rebase", "archive", "history")


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = Path(str(context.get("root") or context.get("os_root") or context.get("zroot") or ".")).resolve()
    docs = root / "docs"

    if not docs.exists():
        return _out(False, ["docs/:MISSING"], [], [], ledger_writer)

    required = [
        docs / "CANONICAL_ONTOLOGY.md",
        docs / "ARCHITECTURE_LITERAL.md",
        docs / "METAPHOR_LAYER.md",
        docs / "INTERPRETATION_CONTRACT.md",
    ]
    missing = [str(p.relative_to(root)) for p in required if not p.exists()]
    if missing:
        return _out(False, [f"DOCS_REQUIRED_MISSING:{m}" for m in missing], [], [], ledger_writer)

    forbidden = _load_forbidden_terms(required[0])

    findings = _scan_docs_for_forbidden(root, forbidden)
    repairs: List[Dict[str, Any]] = []

    if findings:
        repairs.extend(_attempt_repairs(root, findings, forbidden, ledger_writer))
        # Re-scan after repair
        findings = _scan_docs_for_forbidden(root, forbidden)

    ok = len(findings) == 0
    errors = [f"{f['path']}:{f['term']}" for f in findings]

    return _out(ok, errors, findings, repairs, ledger_writer)


def _load_forbidden_terms(ontology_path: Path) -> List[str]:
    txt = ontology_path.read_text(encoding="utf-8", errors="replace")
    terms: List[str] = []

    # Parse a simple bullet list under a heading containing "Forbidden".
    # If parsing fails, fall back to DEFAULT_FORBIDDEN (still strict).
    try:
        blocks = txt.splitlines()
        in_forbidden = False
        for line in blocks:
            if line.strip().lower().startswith("##") and "forbidden" in line.lower():
                in_forbidden = True
                continue
            if in_forbidden and line.strip().startswith("##"):
                break
            if in_forbidden:
                m = re.match(r"^\s*[-*]\s+(.*)$", line)
                if m:
                    term = m.group(1).strip()
                    if term:
                        terms.append(term)
        # Ensure a minimal baseline
        if not terms:
            terms = list(DEFAULT_FORBIDDEN)
    except Exception:
        terms = list(DEFAULT_FORBIDDEN)

    # De-duplicate deterministically
    out: List[str] = []
    for t in terms:
        if t not in out:
            out.append(t)
    return out


def _scan_docs_for_forbidden(root: Path, forbidden: List[str]) -> List[Dict[str, str]]:
    docs = root / "docs"
    findings: List[Dict[str, str]] = []

    # Exclusions: metaphor layer and historical quarantine folder
    exclude_paths = {
        str((docs / "METAPHOR_LAYER.md").resolve()),
        str((docs / "CANONICAL_ONTOLOGY.md").resolve()),
        str((docs / "ARCHITECTURE_LITERAL.md").resolve()),
        str((docs / "INTERPRETATION_CONTRACT.md").resolve()),
    }
    historical_dir = (docs / "_historical").resolve()

    for p in docs.rglob("*.md"):
        rp = p.resolve()
        if str(rp) in exclude_paths:
            continue
        if historical_dir in rp.parents:
            continue

        txt = p.read_text(encoding="utf-8", errors="replace")
        for term in forbidden:
            if term and term in txt:
                findings.append({"path": str(p), "term": term})

    # Stable ordering
    findings.sort(key=lambda d: (d["path"], d["term"]))
    return findings


def _attempt_repairs(root: Path, findings: List[Dict[str, str]], forbidden: List[str], ledger_writer) -> List[Dict[str, Any]]:
    repairs: List[Dict[str, Any]] = []
    docs = root / "docs"
    hist = docs / "_historical"
    hist.mkdir(parents=True, exist_ok=True)

    protected = {
        str((docs / "CANONICAL_ONTOLOGY.md").resolve()),
        str((docs / "ARCHITECTURE_LITERAL.md").resolve()),
    }

    for f in findings:
        path = Path(f["path"])
        term = f["term"]
        rpath = str(path.resolve())

        if rpath in protected:
            # Never auto-edit protected canonical docs
            continue

        # Class A: quarantine historical-looking docs
        if _looks_historical(path):
            dest = hist / path.name
            if dest.exists():
                dest = hist / (path.stem + "__DUP" + path.suffix)
            dest.write_text(_archival_header() + "\n" + path.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
            path.unlink(missing_ok=True)
            rec = {"action": "QUARANTINE", "from": str(path), "to": str(dest), "term": term}
            repairs.append(rec)
            _write_repair_ledger(root, rec)
            if ledger_writer:
                ledger_writer({"event_type": "AUTO_REPAIR", **rec})
            continue

        # Class B: deterministic rewrite if mapping exists
        if term in CLASS_B_REWRITE:
            before = path.read_text(encoding="utf-8", errors="replace")
            after = before.replace(term, CLASS_B_REWRITE[term])
            if after != before:
                after = _autorewrite_header(term) + "\n" + after
                path.write_text(after, encoding="utf-8")
                rec = {"action": "REWRITE", "path": str(path), "term": term, "replacement": CLASS_B_REWRITE[term]}
                repairs.append(rec)
                _write_repair_ledger(root, rec)
                if ledger_writer:
                    ledger_writer({"event_type": "AUTO_REPAIR", **rec})

    return repairs


def _looks_historical(path: Path) -> bool:
    name = path.name.lower()
    return any(h in name for h in HISTORICAL_NAME_HINTS)


def _archival_header() -> str:
    return "<!-- ARCHIVAL_NON_AUTHORITATIVE: quarantined by FAIL-TO-FIX (Class A) -->"


def _autorewrite_header(term: str) -> str:
    return f"<!-- AUTO_REWRITTEN: FAIL-TO-FIX (Class B) replaced forbidden term: {term} -->"


def _write_repair_ledger(root: Path, record: Dict[str, Any]) -> None:
    ledger = root / "ledgers" / "auto_repairs.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    with ledger.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _out(ok: bool, errors: List[str], findings: List[Dict[str, str]], repairs: List[Dict[str, Any]], ledger_writer) -> Dict[str, Any]:
    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": ok,
        "errors": errors,
        "findings": findings,
        "repairs": repairs,
        "mode_active": True,
        "bypass_used": False,
    }
    if ledger_writer is not None:
        ledger_writer({"event_type": "GATE_RESULT", "gate_id": GATE_ID, "ok": ok, "errors": errors, "repairs": repairs})
    return out

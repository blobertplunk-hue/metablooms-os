# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import re


@dataclass(frozen=True)
class Finding:
    path: str
    term: str
    line: int
    excerpt: str


@dataclass(frozen=True)
class Result:
    ok: bool
    findings: List[Finding]
    forbidden_terms: List[str]


def _load_forbidden_terms(ontology_path: Path) -> List[str]:
    text = ontology_path.read_text(encoding="utf-8", errors="replace")
    # Parse bullet list under "Forbidden Terms" heading.
    forbidden: List[str] = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"^##\s+Forbidden Terms", line.strip()):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            m = re.match(r"^\s*-\s+(.*)\s*$", line)
            if m:
                term = m.group(1).strip()
                if term:
                    forbidden.append(term)
    # Deterministic fallback (never empty)
    if not forbidden:
        forbidden = ["Kernel"]
    return forbidden


def validate_docs_forbidden_terms(root: str) -> Result:
    r = Path(root)
    docs = r / "docs"
    ontology = docs / "CANONICAL_ONTOLOGY.md"
    forbidden = _load_forbidden_terms(ontology)

    findings: List[Finding] = []

    # Scan .md excluding METAPHOR_LAYER and historical quarantine.
    for p in docs.rglob("*.md"):
        rel = p.relative_to(r).as_posix()
        if rel == "docs/METAPHOR_LAYER.md":
            continue
        if rel.startswith("docs/_historical/"):
            continue
        # Do not scan ontology itself for forbidden terms (it defines them)
        if rel == "docs/CANONICAL_ONTOLOGY.md":
            continue

        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            for term in forbidden:
                if term and term in line:
                    findings.append(Finding(path=str(p), term=term, line=i, excerpt=line.strip()[:200]))

    return Result(ok=(len(findings) == 0), findings=findings, forbidden_terms=forbidden)

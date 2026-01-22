"""MetaBlooms Canonical RESEARCH Invariant (P0)

If a task is labeled RESEARCH (or research_required==True),
then live external retrieval MUST have occurred in the same turn OR a structured
research evidence pack must be present.

Fail-closed rules:
- If telemetry/sandcrawler_receipts.jsonl exists, research is proven.
- Otherwise, require the structured pack files AND at least one evidence artifact.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List


class ResearchFailClosed(RuntimeError):
    """Raised when research-required work lacks required evidence artifacts."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


STRUCTURED_PACK: List[str] = [
    "research/claims.json",
    "research/citation_map.json",
]

EVIDENCE_ARTIFACT_FLOOR: List[str] = [
    "research/source_excerpts.md",
    "research/evidence_pack.json",
    "research/links.json",
    "research/notes.md",
]


def enforce(context: Dict[str, Any]) -> None:
    """Enforce that research artifacts exist when research is required."""
    if not (context.get("research_required") or str(context.get("mode", "")).upper() == "RESEARCH"):
        return

    repo_root = context.get("repo_root")
    if not repo_root:
        raise ResearchFailClosed("repo_root required for research invariant enforcement")

    root = Path(repo_root)

    # Primary proof: receipts from live retrieval tooling
    if (root / "telemetry" / "sandcrawler_receipts.jsonl").exists():
        return

    structured_ok = all((root / rel).exists() for rel in STRUCTURED_PACK)
    evidence_ok = any((root / rel).exists() for rel in EVIDENCE_ARTIFACT_FLOOR)

    if structured_ok and evidence_ok:
        return

    raise ResearchFailClosed(
        "RESEARCH FAIL-CLOSED — Missing research proof. "
        "Provide telemetry/sandcrawler_receipts.jsonl OR a structured research pack "
        f"({', '.join(STRUCTURED_PACK)}) plus at least one evidence artifact "
        f"({', '.join(EVIDENCE_ARTIFACT_FLOOR)})."
    )

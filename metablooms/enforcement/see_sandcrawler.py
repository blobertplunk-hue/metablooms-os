from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class SEEFailClosed(RuntimeError):
    """Raised when SEE enforcement cannot prove required evidence artifacts exist."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


def enforce(context: Dict[str, Any]) -> None:
    """Fail-closed enforcement for SEE (Sandcrawler Evidence Engine).

    This module does not perform web retrieval; it verifies that SEE evidence artifacts exist.
    """
    repo_root = context.get("repo_root")
    if not repo_root:
        raise SEEFailClosed("repo_root required for SEE enforcement")

    root = Path(repo_root)
    receipts = root / "telemetry" / "sandcrawler_receipts.jsonl"
    if not receipts.exists():
        raise SEEFailClosed("SEE FAIL-CLOSED — Sandcrawler receipts missing: telemetry/sandcrawler_receipts.jsonl")

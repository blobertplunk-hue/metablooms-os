"""MetaBlooms SEE (Sandcrawler Evidence Engine) receipt schema.

Phase: 2 (iteration accounting)

Design goals:
- Deterministic, machine-checkable receipts for each SEE iteration.
- Fail-closed semantics: missing mandatory fields is invalid.
- No external dependencies (stdlib only).

NOTE: This module defines schemas only. It does not perform crawling.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class SEEStopReason(str, Enum):
    SUCCESS = "SUCCESS"
    MAX_ITERATIONS_REACHED = "MAX_ITERATIONS_REACHED"
    BLOCKED_BY_MMD = "BLOCKED_BY_MMD"
    BLOCKED_BY_ECL = "BLOCKED_BY_ECL"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"


@dataclass(frozen=True)
class SEEIterationReceipt:
    """One iteration receipt for SEE loop."""

    loop_id: str
    task_id: str
    iteration: int
    started_utc: str
    ended_utc: str

    # Inputs/outputs snapshots should be small summaries; full raw artifacts should be separate files.
    inputs_snapshot: Dict[str, Any]
    outputs_snapshot: Dict[str, Any]

    # Evidence pointers: list of dicts that should align to EvidencePointer schema (enforced later in gates).
    evidence_pointers: List[Dict[str, Any]]

    # Detector and gate summaries (typed findings live elsewhere; this is a summary snapshot)
    mmd_summary: Dict[str, Any]
    ecl_summary: Dict[str, Any]

    # Errors are recorded but do not imply success.
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SEELoopReceipt:
    """Top-level receipt for the entire loop."""

    loop_id: str
    task_id: str
    started_utc: str
    ended_utc: str
    max_iterations: int
    stop_reason: str

    # References to iteration receipt files
    iteration_receipts: List[str]

    # Summary counts
    iterations_run: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

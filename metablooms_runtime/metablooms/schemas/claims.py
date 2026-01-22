"""Claims schema.

A *Claim* is the unit of truth assessment for SEE.
A ClaimSet is the collection evaluated for task completion.

Fail-closed principle:
- A claim is not "SUPPORTED" unless it has required support evidence.
- "DONE" is not allowed unless every required claim meets its acceptance criteria.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"


@dataclass(frozen=True)
class ClaimAcceptanceCriteria:
    """Acceptance criteria for a claim.

    - minimum_sources: minimum number of distinct sources supporting the claim.
    - source_quality: optional label for how strict source selection should be.
    - freshness_days: optional recency window.
    - must_include: optional list of required keywords/entities in supporting material.
    """

    minimum_sources: int = 1
    source_quality: str = "mixed_ok"  # e.g., authoritative_only | mixed_ok
    freshness_days: Optional[int] = None
    must_include: List[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.minimum_sources < 1:
            raise ValueError("minimum_sources must be >= 1")
        if self.source_quality not in {"authoritative_only", "mixed_ok"}:
            raise ValueError("source_quality must be 'authoritative_only' or 'mixed_ok'")
        if self.freshness_days is not None and self.freshness_days < 0:
            raise ValueError("freshness_days must be >= 0 when provided")


@dataclass
class ClaimSupport:
    """A pointer to evidence supporting (or refuting) a claim."""

    source_id: str
    excerpt_pointer: str  # could be citation handle, or file path + range pointer
    reasoning: str

    def validate(self) -> None:
        if not self.source_id:
            raise ValueError("source_id is required")
        if not self.excerpt_pointer:
            raise ValueError("excerpt_pointer is required")
        if not self.reasoning:
            raise ValueError("reasoning is required")


@dataclass
class Claim:
    claim_id: str
    statement: str
    required: bool = True
    criteria: ClaimAcceptanceCriteria = field(default_factory=ClaimAcceptanceCriteria)

    # Evaluation fields (populated by SEE)
    status: Optional[ClaimStatus] = None
    support: List[ClaimSupport] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)

    def validate_static(self) -> None:
        if not self.claim_id:
            raise ValueError("claim_id is required")
        if not self.statement:
            raise ValueError("statement is required")
        self.criteria.validate()

    def validate_evaluation_fail_closed(self) -> None:
        """Validate that evaluation fields satisfy acceptance criteria."""
        self.validate_static()
        if self.status is None:
            raise ValueError(f"claim {self.claim_id}: status is required")

        # Fail-closed: SUPPORTED requires enough support entries
        if self.status == ClaimStatus.SUPPORTED:
            distinct_sources = {s.source_id for s in self.support}
            if len(distinct_sources) < self.criteria.minimum_sources:
                raise ValueError(
                    f"claim {self.claim_id}: SUPPORTED but has {len(distinct_sources)} distinct sources; "
                    f"requires {self.criteria.minimum_sources}"
                )

        # Validate support entries
        for s in self.support:
            s.validate()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # Enums to string
        d["status"] = self.status.value if self.status is not None else None
        return d


@dataclass
class ClaimSet:
    """A collection of claims with a single pass/fail outcome."""

    claims: List[Claim]

    def validate_static(self) -> None:
        if not self.claims:
            raise ValueError("ClaimSet must contain at least one claim")
        seen = set()
        for c in self.claims:
            c.validate_static()
            if c.claim_id in seen:
                raise ValueError(f"Duplicate claim_id: {c.claim_id}")
            seen.add(c.claim_id)

    def validate_evaluation_fail_closed(self) -> None:
        self.validate_static()
        for c in self.claims:
            # Only required claims must be evaluated and meet criteria
            if c.required:
                c.validate_evaluation_fail_closed()
            else:
                # Optional claims: if status present, it must be consistent
                if c.status is not None:
                    c.validate_evaluation_fail_closed()

    def is_done(self) -> bool:
        """True iff all required claims are SUPPORTED and criteria satisfied."""
        self.validate_evaluation_fail_closed()
        return all((not c.required) or (c.status == ClaimStatus.SUPPORTED) for c in self.claims)

    def to_dict(self) -> Dict[str, Any]:
        return {"claims": [c.to_dict() for c in self.claims]}

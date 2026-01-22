"""MetaBlooms Schemas.

Phase 1 deliverable: typed contracts for Claims, Evidence Packs, and MMD Findings.

Design goals:
- Deterministic, fail-closed parsing/validation.
- Minimal dependencies (Pydantic optional).
- JSON-serializable models.
"""

from .claims import Claim, ClaimSet, ClaimStatus
from .evidence_pack import EvidencePack, EvidenceSource, EvidencePointer, EvidenceScope
from .mmd_finding import MMDAxis, MMDSeverity, MMDFinding

__all__ = [
    "Claim",
    "ClaimSet",
    "ClaimStatus",
    "EvidencePack",
    "EvidenceSource",
    "EvidencePointer",
    "EvidenceScope",
    "MMDAxis",
    "MMDSeverity",
    "MMDFinding",
]

# Phase 2 schemas
from .see_receipt import SEEIterationReceipt, SEELoopReceipt, SEEStopReason  # noqa: F401

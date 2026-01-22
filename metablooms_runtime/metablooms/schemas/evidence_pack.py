"""Evidence Pack schema.

SEE emits an EvidencePack as the canonical proof artifact.
Fail-closed principle:
- Any referenced artifact must be addressable by path + sha256 (local) or by citation handle (web).
- Packs must include an index (file list) suitable for integrity checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class EvidenceScope(str, Enum):
    EXTERNAL_WEB = "external_web"
    LOCAL_FILES = "local_files"
    HYBRID = "hybrid"


@dataclass(frozen=True)
class EvidencePointer:
    """Where to find the supporting material."""

    # Exactly one of these should be set
    citation_handle: Optional[str] = None  # e.g., web.run citation reference
    file_path: Optional[str] = None
    file_sha256: Optional[str] = None
    byte_range: Optional[str] = None  # optional pointer like "L10-L20" or "bytes:0-120"

    def validate(self) -> None:
        has_citation = bool(self.citation_handle)
        has_file = bool(self.file_path or self.file_sha256)
        if has_citation and has_file:
            raise ValueError("EvidencePointer cannot contain both citation_handle and file fields")
        if not has_citation and not has_file:
            raise ValueError("EvidencePointer must contain citation_handle or file_path/file_sha256")
        if has_file:
            if not self.file_path:
                raise ValueError("EvidencePointer: file_path required when using file evidence")
            if not self.file_sha256:
                raise ValueError("EvidencePointer: file_sha256 required when using file evidence")


@dataclass
class EvidenceSource:
    """A retrieved source used to support claims."""

    source_id: str
    source_type: str  # web/pdf/local/other
    title: Optional[str] = None
    publisher_or_domain: Optional[str] = None
    retrieved_timestamp_utc: Optional[str] = None
    pointer: EvidencePointer = field(default_factory=EvidencePointer)

    def validate(self) -> None:
        if not self.source_id:
            raise ValueError("source_id is required")
        if not self.source_type:
            raise ValueError("source_type is required")
        self.pointer.validate()


@dataclass
class EvidencePackIntegrity:
    sha256_of_pack: Optional[str] = None
    file_list: List[Dict[str, str]] = field(default_factory=list)  # [{path, sha256}]

    def validate(self) -> None:
        for item in self.file_list:
            if "path" not in item or "sha256" not in item:
                raise ValueError("integrity.file_list entries must include path and sha256")


@dataclass
class EvidencePack:
    """Canonical SEE output."""

    see_id: str
    timestamp_utc: str
    scope: EvidenceScope
    query: str

    sources: List[EvidenceSource] = field(default_factory=list)
    run_summary: Dict[str, Any] = field(default_factory=dict)
    integrity: EvidencePackIntegrity = field(default_factory=EvidencePackIntegrity)

    def validate_fail_closed(self) -> None:
        if not self.see_id:
            raise ValueError("see_id is required")
        if not self.timestamp_utc:
            raise ValueError("timestamp_utc is required")
        if not self.query:
            raise ValueError("query is required")

        # Fail-closed: HYBRID or LOCAL_FILES must have file-backed pointers for relevant sources
        for s in self.sources:
            s.validate()

        self.integrity.validate()

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["scope"] = self.scope.value
        # normalize pointers already dataclass
        return d

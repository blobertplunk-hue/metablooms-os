# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms ROW/Pipeline Registry Loader (Official v1)

Evidence-first, fail-closed loader for:
- Contracts + routing table
- Artifact-sourced section registries (candidates)
- Canonical registries (runtime)

This module does NOT mutate registries.
Promotion/improvement is handled by build-time tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

class RegistryError(RuntimeError):
    """Raised when required registry artifacts are missing or invalid."""


def _read_json(p: Path) -> Any:
    if not p.exists():
        raise RegistryError(f"Missing required file: {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        raise RegistryError(f"Invalid JSON at {p}: {e}")


def load_official_manifest(root: Path) -> Dict[str, Any]:
    mp = root / "registry" / "rows_pipelines" / "index_manifest.json"
    return _read_json(mp)


def load_contracts(root: Path) -> Dict[str, Any]:
    croot = root / "contracts"
    return {
        "PIPELINE_REGISTRY": _read_json(croot / "PIPELINE_REGISTRY.json"),
        "PIPE_SECTION_SCHEMA": _read_json(croot / "PIPE_SECTION_SCHEMA.json"),
        "ROW_CONTRACT_SCHEMA": _read_json(croot / "ROW_CONTRACT_SCHEMA.json"),
        "ROW_ROUTING_TABLE": _read_json(croot / "ROW_ROUTING_TABLE.json"),
    }


def load_canonical(root: Path) -> Dict[str, Any]:
    base = root / "registry" / "rows_pipelines" / "canonical"
    return {
        "rows": _read_json(base / "rows_canonical.json"),
        "pipelines": _read_json(base / "pipelines_canonical.json"),
        "aliases": _read_json(base / "aliases.json"),
        "supersedes": _read_json(base / "supersedes.json"),
    }


def list_artifact2_sections(root: Path) -> List[str]:
    sdir = root / "registry" / "artifact2_rows_pipelines" / "sections"
    if not sdir.exists():
        return []
    out = []
    for p in sorted(sdir.glob("section_*.*")):
        if p.name.endswith(".registry.json"):
            out.append(p.name.replace(".registry.json",""))
    return out


def load_artifact2_section(root: Path, section_id: str) -> Dict[str, Any]:
    p = root / "registry" / "artifact2_rows_pipelines" / "sections" / f"{section_id}.registry.json"
    return _read_json(p)


def resolve_row_id(name: str, canonical: Dict[str, Any]) -> Optional[str]:
    aliases = (canonical.get("aliases") or {}).get("aliases") or {}
    key = (name or "").strip().lower()
    return aliases.get(key)


def resolve_pipeline_id(name: str, canonical: Dict[str, Any]) -> Optional[str]:
    aliases = (canonical.get("aliases") or {}).get("aliases") or {}
    key = (name or "").strip().lower()
    return aliases.get(key)


def load_runtime_view(root: Path) -> Dict[str, Any]:
    """Single-call loader for runtime consumers.

    Returns contracts + canonical + section inventory.
    Fail-closed if official manifest is missing.
    """
    _ = load_official_manifest(root)  # ensures official structure exists
    contracts = load_contracts(root)
    canonical = load_canonical(root)
    sections = list_artifact2_sections(root)
    return {
        "contracts": contracts,
        "canonical": canonical,
        "sources": {
            "artifact2": {
                "sections": sections
            }
        }
    }

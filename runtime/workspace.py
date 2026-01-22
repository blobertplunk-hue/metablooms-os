"""runtime.workspace

Non-stub workspace abstraction used by MetaBlooms runtime layers.

This module intentionally remains small: it provides a deterministic, filesystem-backed
workspace rooted under the OS tree (or caller-provided root), with a few conveniences
for creating subdirectories in a controlled manner.

This exists primarily to satisfy the NO_PLACEHOLDERS P0 gate by replacing prior silent
stubs with a minimal but functional implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Workspace:
    """A deterministic workspace rooted at an absolute directory."""

    root: Path

    @staticmethod
    def from_root(root: str | Path) -> "Workspace":
        p = Path(root).expanduser().resolve()
        p.mkdir(parents=True, exist_ok=True)
        return Workspace(root=p)

    def ensure_dir(self, rel: str, *, exist_ok: bool = True) -> Path:
        """Ensure a subdirectory exists and return its absolute Path."""
        p = (self.root / rel).resolve()
        # Enforce that the directory is under the workspace root.
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"Workspace path escapes root: {p}")
        p.mkdir(parents=True, exist_ok=exist_ok)
        return p

    def path(self, rel: str = "") -> Path:
        """Return an absolute path under the workspace root (no creation)."""
        p = (self.root / rel).resolve()
        if self.root not in p.parents and p != self.root:
            raise ValueError(f"Workspace path escapes root: {p}")
        return p

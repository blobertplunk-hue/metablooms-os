#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
Canonical Root Enforcement (P0)

- Exactly one canonical OS root: /mnt/data/MetaBlooms_OS
- All writes must stay under canonical root (realpath startswith guard)
- Fail-closed on ambiguity or escape
"""
from __future__ import annotations
import os
from pathlib import Path

CANONICAL_ROOT = Path("/mnt/data/MetaBlooms_OS")

class CanonicalRootError(RuntimeError):
    """Raised when canonical root resolution fails or a path escapes the root."""

def resolve_canonical_root() -> Path:
    """Return the canonical root, fail-closed.

    P0 invariant (historical): canonical root is /mnt/data/MetaBlooms_OS.

    Relocation-safe enhancement:
    - If the historical canonical root does not exist, fall back to the
      extracted bundle root inferred from this file location, *only if*
      the candidate contains an authoritative BOOT contract.
    - Optionally create a symlink at the historical canonical root to
      preserve compatibility for downstream code that hard-codes the path.
    """
    root = CANONICAL_ROOT

    def _has_boot_contract(p: Path) -> bool:
        return (p / "BOOT.md").exists() and (p / "boot_manifest.json").exists() and (p / "BOOT_METABLOOMS.py").exists()

    # 1) Preferred: historical canonical root
    if root.exists() and _has_boot_contract(root):
        return root

    # 2) Relocation-safe fallback: infer from this module path
    inferred = Path(__file__).resolve().parents[1]  # .../MetaBlooms_OS
    if inferred.exists() and _has_boot_contract(inferred):
        # Try to preserve historical path via symlink (best-effort; still safe if it fails)
        try:
            if not root.exists():
                root.parent.mkdir(parents=True, exist_ok=True)
                root.symlink_to(inferred, target_is_directory=True)
        except Exception:
            pass
        return root

    # 3) Fail-closed: root missing or boot contract absent
    if not root.exists():
        raise CanonicalRootError(f"Canonical root missing: {root}")
    raise CanonicalRootError(f"Canonical root missing BOOT contract: {root}")

def assert_within_root(path: os.PathLike | str) -> Path:
    real_root = resolve_canonical_root()
    p = Path(path).expanduser()
    # If relative, interpret relative to canonical root
    if not p.is_absolute():
        p = real_root / p
    real_p = p.resolve()
    real_root_resolved = Path(real_root).resolve()
    root_s = str(real_root_resolved)
    p_s = str(real_p)
    if not (p_s == root_s or p_s.startswith(root_s + os.sep)):
        raise CanonicalRootError(f"WRITE_ESCAPE: {real_p} not under {real_root}")
    return real_p

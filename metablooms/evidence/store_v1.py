"""Evidence Store (v1).

First-class, hash-verified artifact storage.

Security
- All attempt directories are created under the configured evidence root.
- task_id is sanitized into a single safe path component.
- path traversal is fail-closed.
"""

from __future__ import annotations

import hashlib
import os
import shutil
from typing import Dict, List, Optional

from metablooms.concurrency.lock_v1 import FileLock
from metablooms.security.path_safety_v1 import safe_component, safe_join_under


def sha256_file(path: str) -> str:
    """Compute sha256 for a file path (fail-closed)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


class EvidenceStore:
    def __init__(
        self,
        root_dir: str,
        *,
        min_free_bytes: Optional[int] = None,
        max_artifact_bytes: Optional[int] = None,
        max_total_task_bytes: Optional[int] = None,
    ):
        if not isinstance(root_dir, str) or not root_dir.strip():
            raise ValueError("EVIDENCE_ROOT_INVALID")
        self.root_dir = os.path.abspath(root_dir)
        os.makedirs(self.root_dir, exist_ok=True)

        # Resource management (configurable).
        limits = load_resource_limits(
            explicit={
                "min_free_bytes": min_free_bytes,
                "max_artifact_bytes": max_artifact_bytes,
                "max_total_task_bytes": max_total_task_bytes,
            }
        )
        self.min_free_bytes = int(limits["min_free_bytes"])
        self.max_artifact_bytes = int(limits["max_artifact_bytes"])
        self.max_total_task_bytes = int(limits["max_total_task_bytes"])

    def _ensure_free_space(self) -> None:
        free = shutil.disk_usage(self.root_dir).free
        if free < self.min_free_bytes:
            raise ValueError(f"EVIDENCE_DISK_LOW:free={free} required>={self.min_free_bytes}")

    def _task_root(self, safe_id: str) -> str:
        return safe_join_under(self.root_dir, safe_id)

    def _task_bytes(self, safe_id: str) -> int:
        root = self._task_root(safe_id)
        total = 0
        if not os.path.exists(root):
            return 0
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                try:
                    total += os.path.getsize(p)
                except OSError:
                    # Fail-closed: if we cannot stat, treat as unsafe.
                    raise ValueError(f"EVIDENCE_STAT_FAILED:{p}")
        return total

    def _enforce_task_quota(self, safe_id: str) -> None:
        total = self._task_bytes(safe_id)
        if total > self.max_total_task_bytes:
            raise ValueError(f"EVIDENCE_TASK_QUOTA_EXCEEDED:bytes={total} limit={self.max_total_task_bytes}")

    def alloc_attempt_dir(self, task_id: str, iteration: int) -> str:
        safe_id = safe_component(task_id, max_len=80, allow_empty=False)
        if not isinstance(iteration, int) or iteration <= 0:
            raise ValueError("ITERATION_INVALID")

        self._ensure_free_space()

        # Concurrency safety: lock per-task while allocating/writing.
        lock_path = safe_join_under(self.root_dir, os.path.join(safe_id, ".lock"))
        os.makedirs(os.path.dirname(lock_path), exist_ok=True)
        with FileLock(lock_path):
            self._enforce_task_quota(safe_id)

            rel = os.path.join(safe_id, f"iter_{iteration:03d}")
            path = safe_join_under(self.root_dir, rel)
            os.makedirs(path, exist_ok=True)
            return path

    @staticmethod
    def sha256(path: str) -> str:
        return sha256_file(path)

    def list_artifacts_with_hashes(self, paths: List[str]) -> List[Dict[str, str]]:
        out: List[Dict[str, str]] = []
        for p in paths:
            size = os.path.getsize(p)
            if size > self.max_artifact_bytes:
                # Fail-closed on oversized evidence. Resource exhaustion risk.
                raise ValueError(f"EVIDENCE_ARTIFACT_TOO_LARGE:{p} bytes={size} limit={self.max_artifact_bytes}")
            out.append({"path": p, "sha256": self.sha256(p)})
        return out

    def write_receipt(self, attempt_dir: str, receipt: Dict) -> str:
        """Atomic receipt writer with concurrency safety."""
        import json

        if not os.path.isdir(attempt_dir):
            raise ValueError("ATTEMPT_DIR_INVALID")

        self._ensure_free_space()

        path = os.path.join(attempt_dir, "receipt.json")
        tmp = os.path.join(attempt_dir, ".receipt.json.tmp")

        # Acquire lock based on task root.
        # attempt_dir = <root>/<safe_id>/iter_XXX
        safe_id = os.path.basename(os.path.dirname(attempt_dir))
        lock_path = safe_join_under(self.root_dir, os.path.join(safe_id, ".lock"))

        with FileLock(lock_path):
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(receipt, f, indent=2, sort_keys=True)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            self._enforce_task_quota(safe_id)

        return path

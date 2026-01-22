"""File lock (v1).

Purpose
- Provide a cross-process lock for evidence store operations.

Design
- Cross-platform best-effort:
  - POSIX: fcntl.flock
  - Windows: msvcrt.locking

Fail-closed
- If the lock cannot be acquired within timeout, raise LOCK_ACQUIRE_TIMEOUT.
- If the platform locking backend is unavailable, raise LOCK_BACKEND_UNAVAILABLE.

Notes
- This module intentionally avoids third-party dependencies.
"""

from __future__ import annotations

import os
import time
from contextlib import AbstractContextManager


class FileLock(AbstractContextManager):
    """Exclusive lock on a file path.

    On POSIX platforms, uses fcntl.flock.
    On Windows, uses msvcrt.locking.
    """

    def __init__(self, path: str, timeout_seconds: float = 10.0):
        if not isinstance(path, str) or not path.strip():
            raise ValueError("LOCK_PATH_INVALID")
        self.path = path
        self.timeout_seconds = float(timeout_seconds)
        self._fh = None
        self._backend = None  # "posix" | "windows"

    def __enter__(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        self._fh = open(self.path, "a+", encoding="utf-8")

        # Choose backend
        try:
            import fcntl  # type: ignore

            self._backend = "posix"
            self._fcntl = fcntl
        except Exception:
            self._backend = None

        if self._backend is None:
            try:
                import msvcrt  # type: ignore

                self._backend = "windows"
                self._msvcrt = msvcrt
            except Exception:
                self._backend = None

        if self._backend is None:
            raise RuntimeError("LOCK_BACKEND_UNAVAILABLE")

        deadline = time.time() + self.timeout_seconds
        while True:
            try:
                if self._backend == "posix":
                    self._fcntl.flock(self._fh.fileno(), self._fcntl.LOCK_EX | self._fcntl.LOCK_NB)
                else:
                    # Windows msvcrt locking locks a byte-range.
                    # Lock 1 byte at start of file. Must ensure file length >= 1.
                    try:
                        self._fh.seek(0)
                        if self._fh.tell() == 0:
                            self._fh.write("\n")
                            self._fh.flush()
                    except Exception:
                        # Proceed; backend may still lock.
                        pass
                    self._msvcrt.locking(self._fh.fileno(), self._msvcrt.LK_NBLCK, 1)
                return self
            except (BlockingIOError, OSError):
                if time.time() >= deadline:
                    raise TimeoutError("LOCK_ACQUIRE_TIMEOUT")
                time.sleep(0.05)

    def __exit__(self, exc_type, exc, tb):
        try:
            if self._fh is not None:
                try:
                    if self._backend == "posix":
                        self._fcntl.flock(self._fh.fileno(), self._fcntl.LOCK_UN)
                    elif self._backend == "windows":
                        try:
                            self._fh.seek(0)
                        except Exception:
                            pass
                        self._msvcrt.locking(self._fh.fileno(), self._msvcrt.LK_UNLCK, 1)
                finally:
                    self._fh.close()
        finally:
            self._fh = None
            self._backend = None
        return False

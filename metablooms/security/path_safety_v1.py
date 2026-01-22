"""Path safety utilities (v1).

Purpose
- Prevent path traversal and unsafe filesystem writes.
- Provide deterministic sanitization for identifiers used as path components.

Fail-closed
- Reject invalid inputs.
- Ensure all joined paths stay under an explicit root directory.
"""

from __future__ import annotations

import os
import re
from typing import Optional


_ALLOWED = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")


def safe_component(value: str, *, label: str = "component") -> str:
    """Return a sanitized, safe path component.

    Rules:
    - Only [A-Za-z0-9_-]
    - Must start with alnum
    - Length 1..80

    Fail-closed: raises ValueError if the component is invalid.
    """
    if not isinstance(value, str):
        raise ValueError(f"{label} must be str")

    v = value.strip()
    if not _ALLOWED.match(v):
        raise ValueError(f"invalid {label}: {value!r}")

    # Defensive: forbid explicit path separators even if regex would allow none.
    if os.sep in v or (os.altsep and os.altsep in v):
        raise ValueError(f"invalid {label} contains path separator")

    return v


def safe_join_under(root: str, *parts: str, label: Optional[str] = None) -> str:
    """Join parts under root and ensure the resulting path is inside root.

    Fail-closed: raises ValueError if traversal is detected.
    """
    if not isinstance(root, str) or not root:
        raise ValueError("root must be non-empty str")

    root_abs = os.path.abspath(root)
    candidate = os.path.abspath(os.path.join(root_abs, *parts))

    # Normalize with trailing separator to avoid prefix tricks.
    root_prefix = root_abs if root_abs.endswith(os.sep) else root_abs + os.sep
    cand_prefix = candidate if candidate.endswith(os.sep) else candidate + os.sep

    if not cand_prefix.startswith(root_prefix):
        what = label or "path"
        raise ValueError(f"path traversal detected for {what}: {candidate}")

    return candidate

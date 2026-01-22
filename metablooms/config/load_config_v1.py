"""Configuration loader (v1).

This module provides a minimal, deterministic way to tune resource limits
per environment.

Sources (in precedence order):
1) Explicit dict passed by caller
2) Environment variables (MB_*)
3) resource_limits_v1.json profiles
4) Built-in defaults (fail-closed safe-ish)

The intent is to avoid hard-coded constants while keeping behavior reproducible.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ResourceLimits:
    profile: str
    min_free_bytes: int
    max_artifact_bytes: int
    max_total_task_bytes: int


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_resource_limits(
    *,
    explicit: Optional[Dict[str, Any]] = None,
    config_path: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
) -> ResourceLimits:
    """Load ResourceLimits.

    Args:
      explicit: explicit overrides; keys: profile, min_free_bytes, max_artifact_bytes, max_total_task_bytes
      config_path: optional path to resource_limits_v1.json; defaults to this package file.
      env: environment mapping; defaults to os.environ
    """
    env_map = env if env is not None else os.environ

    # 1) explicit dict
    explicit = dict(explicit or {})

    # 2) config file
    if config_path:
        cfg_path = Path(config_path)
    else:
        cfg_path = Path(__file__).with_name("resource_limits_v1.json")

    cfg = _read_json(cfg_path)
    profiles = cfg.get("profiles", {})
    defaults = cfg.get("defaults", {})
    env_overrides = cfg.get("env_overrides", {})

    # base profile
    profile = str(explicit.get("profile") or env_map.get("MB_RESOURCE_PROFILE") or defaults.get("profile") or "desktop")
    base = profiles.get(profile) or profiles.get("desktop") or {}

    # start with base
    merged: Dict[str, Any] = {
        "profile": profile,
        "min_free_bytes": int(base.get("min_free_bytes", 200_000_000)),
        "max_artifact_bytes": int(base.get("max_artifact_bytes", 20_000_000)),
        "max_total_task_bytes": int(base.get("max_total_task_bytes", 200_000_000)),
    }

    # env overrides (declared in config)
    for env_key, field in env_overrides.items():
        if env_key in env_map and env_map.get(env_key) not in (None, ""):
            if field == "profile":
                merged["profile"] = str(env_map[env_key])
            else:
                merged[field] = int(env_map[env_key])

    # explicit overrides win
    for k in ("profile", "min_free_bytes", "max_artifact_bytes", "max_total_task_bytes"):
        if k in explicit and explicit[k] is not None:
            merged[k] = str(explicit[k]) if k == "profile" else int(explicit[k])

    return ResourceLimits(
        profile=str(merged["profile"]),
        min_free_bytes=int(merged["min_free_bytes"]),
        max_artifact_bytes=int(merged["max_artifact_bytes"]),
        max_total_task_bytes=int(merged["max_total_task_bytes"]),
    )

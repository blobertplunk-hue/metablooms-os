# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json
from pathlib import Path

def run():
    root = Path(__file__).resolve().parents[1]
    reg_path = root / "MODULE_REGISTRY.json"
    if not reg_path.exists():
        raise RuntimeError("MODULE_REGISTRY_MISSING")

    try:
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise RuntimeError(f"MODULE_REGISTRY_INVALID_JSON: {e}")

    if reg.get("format_version") != "1.0":
        raise RuntimeError("MODULE_REGISTRY_SCHEMA_FAIL: format_version must be 1.0")

    modules = reg.get("modules")
    if not isinstance(modules, list) or not modules:
        raise RuntimeError("MODULE_REGISTRY_SCHEMA_FAIL: modules must be non-empty list")

    ids = [m.get("module_id") for m in modules]
    if any((not isinstance(i,str) or not i) for i in ids):
        raise RuntimeError("MODULE_REGISTRY_SCHEMA_FAIL: module_id required")
    if len(set(ids)) != len(ids):
        raise RuntimeError("MODULE_REGISTRY_SCHEMA_FAIL: duplicate module_id")

    idset = set(ids)

    # validate each module required fields and entrypoint existence
    for m in modules:
        for key in ["purpose","entrypoint","activation","dependencies","cost_profile","telemetry"]:
            if key not in m:
                raise RuntimeError(f"MODULE_REGISTRY_SCHEMA_FAIL: {m.get('module_id')} missing {key}")

        ep = m["entrypoint"]
        ep_path = ep.get("path")
        ep_type = ep.get("type")
        if ep_type not in ("package","file","script"):
            raise RuntimeError("MODULE_REGISTRY_SCHEMA_FAIL: entrypoint.type invalid")

        resolved = root / ep_path
        if not resolved.exists():
            raise RuntimeError(f"MODULE_ENTRYPOINT_MISSING_ON_DISK: {m.get('module_id')} -> {ep_path}")

        if ep_type == "package":
            # package dir must have __init__.py
            if resolved.is_dir() and not (resolved / "__init__.py").exists():
                # allow packages where __init__.py exists at modules/__init__.py and subdir is namespace,
                # but prefer explicit __init__.py for auditability
                raise RuntimeError(f"MODULE_ENTRYPOINT_MISSING_ON_DISK: {m.get('module_id')} package missing __init__.py at {ep_path}")

        act = m["activation"]
        if act.get("default") == "conditional":
            conds = act.get("conditions")
            if not isinstance(conds, list) or not conds:
                raise RuntimeError(f"MODULE_ACTIVATION_CONDITIONAL_MISSING_CONDITIONS: {m.get('module_id')}")

        deps = m["dependencies"]
        hard = deps.get("hard", [])
        if any(d not in idset for d in hard):
            raise RuntimeError(f"MODULE_DEPENDENCY_UNKNOWN: {m.get('module_id')}")

    return "MODULE_REGISTRY_SCHEMA_V1_OK"

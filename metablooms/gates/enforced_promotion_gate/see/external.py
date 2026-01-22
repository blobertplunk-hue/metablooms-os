import json
from typing import List, Tuple

PRIMARY_TYPES = {"docs", "release_notes", "standard", "security_advisory"}
CORROBORATING_TYPES = {"issue", "pull_request", "repo_file", "repo_commit", "blog", "package_registry", "other"}

def load_external_items(paths: List[str]) -> List[dict]:
    items: List[dict] = []
    for p in paths or []:
        with open(p, "r", encoding="utf-8") as f:
            items.append(json.load(f))
    return items

def validate_external_items_minimum(items: List[dict]) -> Tuple[bool, str]:
    if len(items) < 2:
        return False, "External SEE required but missing (need >= 2 items: 1 primary HIGH + 1 corroborating MED+)"
    has_primary_high = any((it.get("source_type") in PRIMARY_TYPES) and (it.get("confidence") == "HIGH") for it in items)
    has_corroborating_med = any((it.get("source_type") in CORROBORATING_TYPES) and (it.get("confidence") in ("MED", "HIGH")) for it in items)
    if not has_primary_high:
        return False, "External SEE minimum not met (missing primary HIGH item)"
    if not has_corroborating_med:
        return False, "External SEE minimum not met (missing corroborating MED+ item)"
    return True, "OK"

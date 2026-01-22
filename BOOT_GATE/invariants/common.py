"""Common logic for boot P0 invariants (FullTeeth v2).

Non-prescriptive: enforcement only.
"""

from __future__ import annotations

import datetime
import glob
import hashlib
import json
import os
from typing import Any, Dict, List, Tuple


def _utc_now() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _write_text(path: str, text: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    b = text.encode("utf-8")
    with open(path, "wb") as f:
        f.write(b)
    return _sha256_bytes(b)


def _append_jsonl(path: str, obj: Dict[str, Any]) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
    with open(path, "ab") as f:
        f.write(line)
    return _sha256_bytes(line)


def discover_canonical_os_candidates(scan_root: str = "/mnt/data") -> List[str]:
    """Deterministically scan /mnt/data for canonical OS candidates.

    Candidates include:
    - ZIP archives containing 'MetaBlooms_OS' in name
    - Directories that contain a BOOT_METABLOOMS.py
    """

    candidates: List[str] = []

    # ZIP candidates
    for p in glob.glob(os.path.join(scan_root, "**", "*.zip"), recursive=True):
        bn = os.path.basename(p)
        if "MetaBlooms_OS" in bn:
            candidates.append(os.path.abspath(p))

    # Extracted OS candidates
    for p in glob.glob(os.path.join(scan_root, "**", "BOOT_METABLOOMS.py"), recursive=True):
        candidates.append(os.path.abspath(os.path.dirname(p)))

    # Stable ordering for determinism
    candidates = sorted(list(dict.fromkeys(candidates)))
    return candidates


def enforce_inv_boot_p0_locate_os(inv_id: str, trigger: str) -> Tuple[bool, Dict[str, Any]]:
    """Implements the invariant statement in FullTeeth v2 docs.

    PASS iff at least one candidate is discovered.
    Always writes:
    - OS_DISCOVERY_ATTEMPT record
    - resistance_ledger.jsonl entry
    On FAIL also writes:
    - INV_<id>_FAIL.md artifact
    """

    ts = _utc_now()
    discovered = discover_canonical_os_candidates("/mnt/data")

    # Evidence artifact: OS discovery attempt
    discovery_path = "/mnt/data/metablooms_boot_audit/OS_DISCOVERY_ATTEMPT.json"
    discovery_obj = {
        "kind": "OS_DISCOVERY_ATTEMPT",
        "inv_id": inv_id,
        "trigger": trigger,
        "timestamp": ts,
        "scan_root": "/mnt/data",
        "discovered_paths": discovered,
    }
    os.makedirs(os.path.dirname(discovery_path), exist_ok=True)
    with open(discovery_path, "w", encoding="utf-8") as f:
        json.dump(discovery_obj, f, indent=2, ensure_ascii=False)

    # Resistance ledger
    resistance_ledger = "/mnt/data/metablooms_ledgers/resistance_ledger.jsonl"

    if not discovered:
        fail_artifact = f"/mnt/data/metablooms_boot_audit/{inv_id}_FAIL.md"
        _write_text(
            fail_artifact,
            "\n".join(
                [
                    f"INV_ID: {inv_id}",
                    "OUTCOME: FAIL_CLOSED",
                    f"TIMESTAMP: {ts}",
                    "REASON: OS discovery found zero canonical candidates under /mnt/data.",
                    "NOTE: This artifact is produced by executable invariant enforcement.",
                ]
            )
            + "\n",
        )

        _append_jsonl(
            resistance_ledger,
            {
                "inv_id": inv_id,
                "trigger": trigger,
                "discovered_paths": discovered,
                "outcome": "FAIL",
                "timestamp": ts,
            },
        )
        return False, {"discovered_paths": discovered, "discovery_artifact": discovery_path}

    _append_jsonl(
        resistance_ledger,
        {
            "inv_id": inv_id,
            "trigger": trigger,
            "discovered_paths": discovered,
            "outcome": "PASS",
            "timestamp": ts,
        },
    )
    return True, {"discovered_paths": discovered, "discovery_artifact": discovery_path}

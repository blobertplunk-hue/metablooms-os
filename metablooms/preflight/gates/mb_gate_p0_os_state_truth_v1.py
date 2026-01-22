from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


GATE_ID = "P0.OS.STATE.TRUTH.V1"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _find_canonical_zip(mnt: Path) -> Optional[Path]:
    """Fail-closed: canonical zip must be uniquely identifiable."""
    # Deterministic selection: the canonical Whole OS bundle is the only valid
    # P0 boot target. Additional ZIPs (delta packs, invariant packs, audits)
    # must not be treated as bootable OS candidates.
    zips = sorted(mnt.glob("MetaBlooms_OS_WHOLEOS_*.zip"))
    if len(zips) != 1:
        return None
    return zips[0]


def _safe_extract(zip_path: Path, extract_root: Path) -> None:
    """Extract zip into extract_root (best-effort clean).

    Teeth: prefers self-heal via deterministic rehydrate.
    Safety: does not attempt partial overwrites; rebuilds directory contents.
    """
    if extract_root.exists():
        # Remove contents but keep directory.
        for p in sorted(extract_root.rglob("*"), reverse=True):
            if p.is_file() or p.is_symlink():
                p.unlink(missing_ok=True)
            elif p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    pass
    extract_root.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_root)


def run_gate(run_ctx: Dict[str, object]) -> Dict[str, object]:
    """OS State Truth gate.

    Contract: treat /mnt/data as the only truth.
    - If canonical zip is missing/ambiguous -> fail-closed.
    - If extracted root / entrypoint / sentinel mismatch -> attempt deterministic rehydrate.
    """

    mnt = Path("/mnt/data")

    # Safety: do not attempt to delete/overwrite the currently executing repo
    # tree. This gate writes/rehydrates into a dedicated extraction root.
    # Default rehydrate target is a separate staging root under /mnt/data.
    extract_root = Path(str(run_ctx.get("mb_os_state_truth_extract_root", "/mnt/data/metablooms_os_rehydrated")))
    exec_root = Path(str(run_ctx.get("root", ""))).resolve() if run_ctx.get("root") else None
    sentinel_path = extract_root / ".mb_state_truth.json"
    boot_path = extract_root / "BOOT_METABLOOMS.py"

    zip_path = _find_canonical_zip(mnt)
    if not zip_path:
        return {
            "pass": False,
            "reason": "CANONICAL_OS_ZIP_NOT_FOUND_OR_AMBIGUOUS",
            "evidence": {
                "mnt": str(mnt),
                "candidate_zips": sorted([p.name for p in mnt.glob("MetaBlooms_OS_WHOLEOS_*.zip")]),
            },
        }

    zip_sha = _sha256(zip_path)

    needs_rehydrate = (
        not extract_root.exists()
        or not boot_path.exists()
        or not sentinel_path.exists()
    )

    if not needs_rehydrate:
        try:
            sentinel = json.loads(sentinel_path.read_text(encoding="utf-8"))
            if (
                sentinel.get("canonical_zip") != zip_path.name
                or sentinel.get("canonical_zip_sha256") != zip_sha
                or sentinel.get("boot_entrypoint") != "BOOT_METABLOOMS.py"
            ):
                needs_rehydrate = True
            else:
                # If entrypoint exists, ensure sentinel binds to actual on-disk bytes.
                if sentinel.get("boot_entrypoint_sha256") != _sha256(boot_path):
                    needs_rehydrate = True
        except Exception:
            needs_rehydrate = True

    if needs_rehydrate:
        # Never destructively rehydrate the currently executing repo root.
        if exec_root is not None and extract_root.resolve() == exec_root:
            return {
                "pass": False,
                "reason": "UNSAFE_REHYDRATE_TARGET_EQUALS_EXEC_ROOT",
                "evidence": {"exec_root": str(exec_root), "extract_root": str(extract_root)},
            }
        try:
            _safe_extract(zip_path, extract_root)
        except Exception as e:
            return {
                "pass": False,
                "reason": "OS_REHYDRATION_FAILED",
                "evidence": {"error": f"{type(e).__name__}:{e}"},
            }

        if not boot_path.exists():
            return {
                "pass": False,
                "reason": "BOOT_ENTRYPOINT_MISSING_AFTER_REHYDRATE",
                "evidence": {"expected": str(boot_path)},
            }

        sentinel_obj = {
            "canonical_zip": zip_path.name,
            "canonical_zip_sha256": zip_sha,
            "extracted_root": str(extract_root),
            "boot_entrypoint": "BOOT_METABLOOMS.py",
            "boot_entrypoint_sha256": _sha256(boot_path),
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        }
        sentinel_path.write_text(json.dumps(sentinel_obj, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "pass": True,
        "reason": "OS_STATE_TRUTH_VERIFIED",
        "evidence": {
            "canonical_zip": zip_path.name,
            "canonical_zip_sha256": zip_sha,
            "extracted_root": str(extract_root),
            "sentinel": str(sentinel_path),
        },
    }

#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Core Runtime Authority (MCRA)

Purpose
-------
A fail-closed *external* authority layer that bridges:
  (a) what was decided (contracts / invariants / manifests)
  (b) what is physically embodied in a shipped OS bundle

This tool is intentionally boring:
- No "should work" claims.
- No in-place mutation of the provided OS root.
- Ship = build a new ZIP only after mechanical gates pass.

Core responsibilities
---------------------
1) Build workspace from a source OS root (copy-on-write into a temp workdir)
2) Apply one or more Delta directories (each with a DELTA_MANIFEST.json)
3) Enforce invariants:
   - immutable entrypoint exists at bundle root
   - required doctrine files are present
   - SHIP_MANIFEST.json exists and matches real files
   - optional module registry / decision log are emitted
4) Run a *mechanical* preflight (file-level gates) and emit a proof report
5) Ship a ZIP (and optional proof bundle) with SHA256s

Notes
-----
- This module does not assume a particular MetaBlooms internal layout beyond
  the required files listed below.
- If you want stronger invariants, add them as machine-readable policies;
  markdown-only contracts are human-readable but not sufficient for enforcement.

"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# -----------------------------
# HARD GATES (fail-closed)
# -----------------------------

REQUIRED_ENTRYPOINT = "BOOT_METABLOOMS.py"
SHIP_MANIFEST_NAME = "SHIP_MANIFEST.json"

# These are the *minimum* governance doctrine artifacts the bundle must contain.
REQUIRED_DOCTRINE_FILES = [
    "MB_BOOT_CONTRACT.md",
    "MB_SHIP_INVARIANTS.md",
    "MB_DELTA_PROTOCOL.md",
    "MB_MODULE_REGISTRY.md",
    "MB_CORE_RUNTIME_AUTHORITY.md",
    "MB_ARTIFACT_TYPES_CANONICAL.md",
    "MB_DECISION_LOG_SCHEMA.json",
]

# Optional, but strongly recommended for machine enforcement.
OPTIONAL_MACHINE_ARTIFACTS = [
    "MODULE_REGISTRY.json",
    "DECISION_LOG.ndjson",
]


# -----------------------------
# Exceptions / fail-closed
# -----------------------------

class FailClosed(RuntimeError):
    """Fail-closed error.

    Raised when a P0/P1 invariant or mechanical gate fails.
    """


def fatal(msg: str) -> None:
    raise FailClosed(msg)


# -----------------------------
# Hashing / IO
# -----------------------------


def sha256_bytes(b: bytes) -> str:
    h = hashlib.sha256()
    h.update(b)
    return h.hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def now_utc_stamp() -> str:
    return _dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")


def read_json(path: Path, *, context: str) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        fatal(f"Invalid JSON for {context}: {path} :: {e}")


def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# -----------------------------
# Workdir (no in-place mutation)
# -----------------------------


def copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        fatal(f"OS root does not exist: {src}")
    if not src.is_dir():
        fatal(f"OS root is not a directory: {src}")

    # Copy including symlinks as symlinks; ignore common junk.
    def _ignore(_dir, names):
        junk = {".DS_Store", "__pycache__", ".pytest_cache"}
        return [n for n in names if n in junk]

    shutil.copytree(src, dst, symlinks=True, ignore=_ignore)


# -----------------------------
# Delta format (minimal)
# -----------------------------


def apply_delta(delta_dir: Path, target_root: Path) -> Tuple[str, List[str]]:
    """Apply a delta directory onto target_root. Returns (delta_id, files_applied)."""
    if not delta_dir.exists() or not delta_dir.is_dir():
        fatal(f"Delta dir missing or not a directory: {delta_dir}")

    manifest = delta_dir / "DELTA_MANIFEST.json"
    if not manifest.exists():
        fatal(f"Delta missing DELTA_MANIFEST.json: {delta_dir}")

    spec = read_json(manifest, context="DELTA_MANIFEST")

    delta_id = str(spec.get("delta_id") or delta_dir.name)
    files = spec.get("files")
    if not isinstance(files, list) or not files:
        fatal(f"DELTA_MANIFEST.json missing non-empty 'files' list: {manifest}")

    applied: List[str] = []

    for relpath in files:
        if not isinstance(relpath, str) or relpath.strip() == "":
            fatal(f"Delta has invalid file path entry: {relpath!r} in {manifest}")
        # Prevent path traversal
        if relpath.startswith("/") or ".." in Path(relpath).parts:
            fatal(f"Delta file path not allowed (path traversal): {relpath}")

        src = delta_dir / relpath
        if not src.exists() or not src.is_file():
            fatal(f"Delta references missing file: {src}")

        dst = target_root / relpath
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())
        applied.append(relpath)

    return delta_id, applied


# -----------------------------
# Validation gates
# -----------------------------


def validate_entrypoint(root: Path) -> None:
    ep = root / REQUIRED_ENTRYPOINT
    if not ep.exists() or not ep.is_file():
        fatal(f"Missing required entrypoint at bundle root: {REQUIRED_ENTRYPOINT}")


def validate_doctrine(root: Path) -> None:
    missing = [name for name in REQUIRED_DOCTRINE_FILES if not (root / name).exists()]
    if missing:
        fatal(f"Missing required governance doctrine files: {missing}")


def validate_ship_manifest(root: Path) -> Dict[str, str]:
    """Validate SHIP_MANIFEST.json and return {relpath: sha256} from manifest."""
    manifest_path = root / SHIP_MANIFEST_NAME
    if not manifest_path.exists():
        fatal(f"{SHIP_MANIFEST_NAME} is required but missing")

    m = read_json(manifest_path, context="SHIP_MANIFEST")

    files = m.get("files")
    if not isinstance(files, list) or not files:
        fatal(f"{SHIP_MANIFEST_NAME} must contain non-empty 'files' list")

    # Optional: if hashes are provided, enforce them; if not, compute them.
    hashes_in = m.get("sha256")
    hashes: Dict[str, str] = {}

    for rel in files:
        if not isinstance(rel, str) or rel.strip() == "":
            fatal(f"SHIP_MANIFEST contains invalid file path entry: {rel!r}")
        if rel.startswith("/") or ".." in Path(rel).parts:
            fatal(f"SHIP_MANIFEST path traversal not allowed: {rel}")

        p = root / rel
        if not p.exists() or not p.is_file():
            fatal(f"SHIP_MANIFEST references missing file: {rel}")

        h = sha256_file(p)
        hashes[rel] = h

    if isinstance(hashes_in, dict) and hashes_in:
        # Strict verify provided hashes.
        mismatched = []
        for rel, expected in hashes_in.items():
            if rel not in hashes:
                mismatched.append((rel, "not_in_files", expected))
                continue
            if expected != hashes[rel]:
                mismatched.append((rel, hashes[rel], expected))
        if mismatched:
            fatal(f"SHIP_MANIFEST sha256 mismatches: {mismatched[:10]}" + (" ..." if len(mismatched) > 10 else ""))

    return hashes


def validate_size_sanity(root: Path, *, min_files: int = 10) -> None:
    # This is not a primary truth signal, but it catches absurd skeletons.
    count = sum(1 for p in root.rglob("*") if p.is_file())
    if count < min_files:
        fatal(f"OS root contains too few files ({count}); looks like a skeleton")


# -----------------------------
# Decision log
# -----------------------------


def append_decision_log(root: Path, event: dict) -> None:
    log_path = root / "DECISION_LOG.ndjson"
    line = json.dumps(event, sort_keys=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# -----------------------------
# ZIP build + proof
# -----------------------------


def build_zip_from_root(root: Path, out_zip: Path) -> Dict[str, str]:
    """Build a ZIP and return file hashes for the ZIP entries."""
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    if out_zip.exists():
        out_zip.unlink()

    entry_hashes: Dict[str, str] = {}

    with zipfile.ZipFile(out_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            if p.is_file():
                rel = str(p.relative_to(root))
                z.write(p, rel)
                entry_hashes[rel] = sha256_file(p)

    return entry_hashes


def build_proof_bundle(
    *,
    work_root: Path,
    out_dir: Path,
    os_zip: Path,
    ship_hash: str,
    ship_manifest_hashes: Dict[str, str],
    applied_deltas: List[dict],
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    proof_path = out_dir / f"BOOT_PROOF_{now_utc_stamp()}.json"

    proof = {
        "timestamp_utc": now_utc_stamp(),
        "entrypoint": REQUIRED_ENTRYPOINT,
        "os_zip": os_zip.name,
        "os_zip_sha256": ship_hash,
        "ship_manifest_file": SHIP_MANIFEST_NAME,
        "ship_manifest_sha256_map": ship_manifest_hashes,
        "applied_deltas": applied_deltas,
        "workspace_file_count": sum(1 for p in work_root.rglob("*") if p.is_file()),
    }

    write_json(proof_path, proof)
    return proof_path


# -----------------------------
# Main pipeline
# -----------------------------


def run_pipeline(
    *,
    os_root: Path,
    out_zip: Path,
    delta_dirs: List[Path],
    proof_dir: Optional[Path],
) -> Tuple[Path, Optional[Path]]:

    stamp = now_utc_stamp()

    with tempfile.TemporaryDirectory(prefix="metablooms_mcra_") as tmp:
        work_root = Path(tmp) / "os_work"
        copy_tree(os_root, work_root)

        applied: List[dict] = []
        for d in delta_dirs:
            delta_id, files = apply_delta(d, work_root)
            applied.append({"delta_id": delta_id, "files_applied": files})

        # Mechanical gates
        validate_size_sanity(work_root)
        validate_entrypoint(work_root)
        validate_doctrine(work_root)
        ship_manifest_hashes = validate_ship_manifest(work_root)

        # Record decision log event (append-only)
        append_decision_log(
            work_root,
            {
                "ts_utc": stamp,
                "event": "SHIP_PIPELINE_PASS",
                "entrypoint": REQUIRED_ENTRYPOINT,
                "applied_deltas": [a["delta_id"] for a in applied],
                "out_zip": str(out_zip),
            },
        )

        # Build
        entry_hashes = build_zip_from_root(work_root, out_zip)
        zip_hash = sha256_file(out_zip)

        proof_path: Optional[Path] = None
        if proof_dir is not None:
            proof_path = build_proof_bundle(
                work_root=work_root,
                out_dir=proof_dir,
                os_zip=out_zip,
                ship_hash=zip_hash,
                ship_manifest_hashes=ship_manifest_hashes,
                applied_deltas=applied,
            )

        # Also write a small sidecar hash file for the shipped zip.
        out_zip.with_suffix(out_zip.suffix + ".sha256").write_text(
            f"{zip_hash}  {out_zip.name}\n", encoding="utf-8"
        )

        # Return outputs (note: work_root is temp, so only out_zip/proof survive)
        return out_zip, proof_path


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="MetaBlooms Core Runtime Authority: apply deltas, enforce invariants, ship OS zip (fail-closed)."
    )
    p.add_argument("os_root", help="Path to extracted canonical OS root directory")
    p.add_argument("out_zip", help="Output ZIP path")
    p.add_argument(
        "--delta",
        action="append",
        default=[],
        help="Delta directory path (repeatable). Each must contain DELTA_MANIFEST.json",
    )
    p.add_argument(
        "--proof-dir",
        default=None,
        help="Optional directory to write proof JSON (outside the zip)",
    )
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    try:
        out_zip, proof = run_pipeline(
            os_root=Path(args.os_root).resolve(),
            out_zip=Path(args.out_zip).resolve(),
            delta_dirs=[Path(d).resolve() for d in args.delta],
            proof_dir=Path(args.proof_dir).resolve() if args.proof_dir else None,
        )
    except FailClosed as e:
        print(f"\nBOOT_FAILED: {e}")
        return 2

    print("\nSHIP_OK")
    print(f"OS_ZIP: {out_zip}")
    print(f"OS_ZIP_SHA256: {sha256_file(out_zip)}")
    if proof:
        print(f"PROOF_JSON: {proof}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

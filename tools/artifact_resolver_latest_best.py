#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
artifact_resolver_latest_best.py (Selector v1.0)

Deterministically identify "latest" and "best" MetaBlooms cumulative OS ZIPs from a directory.
Prefers explicit metadata sidecars; falls back to evidence-based selection if metadata is missing.

Usage:
  python artifact_resolver_latest_best.py /path/to/artifacts

Outputs:
  - LATEST.json (canonical pointers)
  - latest_best_proof.json (machine-readable proof)
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib, json, re, sys, time
from typing import Optional, Dict, Any, List, Tuple

SEMVER = re.compile(r"v(\d+)_(\d+)_(\d+)")

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_semver_from_name(name: str) -> Optional[Tuple[int,int,int]]:
    m = SEMVER.search(name)
    return (int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None

@dataclass(frozen=True)
class Candidate:
    zip_path: Path
    version: Tuple[int,int,int]
    sha256: Optional[str]
    meta: Optional[Dict[str, Any]]
    evidence: Dict[str, Any]

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8").strip()

def has_boot_proof(dirp: Path, zip_name: str) -> List[str]:
    hits = []
    for p in dirp.glob("*boot_proof*.json"):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            # common keys we used in proofs
            if obj.get("output_zip") == zip_name or obj.get("source_zip") == zip_name or obj.get("output_zip","") == zip_name:
                hits.append(p.name)
            # some proofs store produced_zip
            if obj.get("produced_zip") == zip_name:
                hits.append(p.name)
        except Exception:
            continue
    return sorted(set(hits))

def load_meta(zip_path: Path) -> Optional[Dict[str, Any]]:
    meta_path = zip_path.with_suffix(zip_path.suffix + ".meta.json")
    if not meta_path.exists():
        return None
    return json.loads(meta_path.read_text(encoding="utf-8"))

def verify_sha256(zip_path: Path) -> Optional[str]:
    sha_path = zip_path.with_suffix(zip_path.suffix + ".sha256")
    if not sha_path.exists():
        return None
    expected = read_text(sha_path)
    computed = sha256_file(zip_path)
    if expected != computed:
        raise RuntimeError(f"SHA256_MISMATCH: {zip_path.name}")
    return computed

def score(meta: Optional[Dict[str,Any]]) -> int:
    # Higher is better
    if not meta:
        return 0
    status = meta.get("governance_status","unknown")
    return {
        "deprecated": -10,
        "unknown": 0,
        "boot_verified": 10,
        "baseline_frozen": 20,
    }.get(status, 0)

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    zips = sorted(root.glob("MetaBlooms_OS_CUMULATIVE_WITH_ZOOP_LEDGERGATE_v*.zip"))
    cands: List[Candidate] = []
    for z in zips:
        v = parse_semver_from_name(z.name)
        if not v:
            continue
        meta = load_meta(z)
        sha = None
        try:
            sha = verify_sha256(z)
        except RuntimeError as e:
            # hard fail-closed
            raise
        evidence = {
            "sha256_verified": bool(sha),
            "boot_proof_files": has_boot_proof(root, z.name),
            "meta_present": bool(meta),
        }
        cands.append(Candidate(z, v, sha, meta, evidence))

    if not cands:
        raise RuntimeError("NO_CANDIDATES_FOUND")

    # latest: highest semver among boot-verified (meta) else evidence boot proof
    def boot_verified(c: Candidate) -> bool:
        if c.meta and c.meta.get("governance_status") in ("boot_verified","baseline_frozen"):
            return True
        return len(c.evidence["boot_proof_files"]) > 0

    verified = [c for c in cands if boot_verified(c)]
    if not verified:
        raise RuntimeError("NO_BOOT_VERIFIED_CANDIDATES")

    latest = max(verified, key=lambda c: c.version)

    # best: prefer governance score, then semver
    best = max(verified, key=lambda c: (score(c.meta), c.version))

    latest_json = {
        "selector_version": "1.0",
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "latest_os_zip": latest.zip_path.name,
        "best_os_zip": best.zip_path.name,
        "baseline_v1_os_zip": None,  # set explicitly by governance when freezing baseline
        "selection_evidence": {
            "latest": latest.evidence,
            "best": best.evidence,
        },
    }

    (root/"LATEST.json").write_text(json.dumps(latest_json, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    proof = {
        "selector_version": "1.0",
        "root": str(root.resolve()),
        "candidates": [
            {
                "zip": c.zip_path.name,
                "version": ".".join(map(str,c.version)),
                "sha256": c.sha256,
                "meta_present": bool(c.meta),
                "governance_status": (c.meta.get("governance_status") if c.meta else None),
                "evidence": c.evidence,
            }
            for c in sorted(cands, key=lambda c: c.version)
        ],
        "latest": latest.zip_path.name,
        "best": best.zip_path.name,
    }
    (root/"latest_best_proof.json").write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()

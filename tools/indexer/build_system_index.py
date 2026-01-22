#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms System Index Builder

Purpose:
  - Deterministically produce SYSTEM_INDEX.json for a MetaBlooms OS folder.
  - Provide a fast, authoritative 'where is what' lookup to avoid re-scanning bundles.

Usage:
  python tools/indexer/build_system_index.py --root . --out SYSTEM_INDEX.json

Notes:
  - Does NOT modify runtime behavior. It is a build/maintenance utility.
  - Designed for fail-closed workflows: you can diff/verify index output before shipping.
"""

from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

KIND_RULES = [
    (lambda rel: rel == "BOOT_METABLOOMS.py", "entrypoint"),
    (lambda rel: rel in {"SHIP_MANIFEST.json","MODULE_REGISTRY.json","MB_RUNTIME_CONFIG.json","sandcrawler_state/SANDCRAWLER_READY.json"}, "runtime_config"),
    (lambda rel: rel.startswith("modules/"), "module_code"),
    (lambda rel: rel.startswith("MB_") and rel.endswith(".md"), "governance_doctrine"),
    (lambda rel: rel.endswith(".pyc") or rel.startswith("__pycache__/") or "/__pycache__/" in rel, "build_artifact"),
    (lambda rel: rel.upper().endswith("SCHEMA.json"), "schema"),
]

def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def classify(rel: str) -> str:
    for pred, kind in KIND_RULES:
        if pred(rel):
            return kind
    return "other"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root directory of the OS")
    ap.add_argument("--out", required=True, help="Path to write SYSTEM_INDEX.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out = Path(args.out).resolve()

    entries = []
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        rel = p.relative_to(root).as_posix()
        entries.append({
            "path": rel,
            "sha256": sha256_file(p),
            "bytes": p.stat().st_size,
            "ext": p.suffix.lower(),
            "kind": classify(rel),
        })

    index = {
        "system": "MetaBlooms",
        "index_version": "1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00","Z"),
        "root": root.as_posix(),
        "file_count": len(entries),
        "paths": entries,
        "lookup": {
            "entrypoint": "BOOT_METABLOOMS.py",
            "ship_manifest": "SHIP_MANIFEST.json",
            "module_registry": "MODULE_REGISTRY.json",
            "governance_docs": [e["path"] for e in entries if e["kind"] == "governance_doctrine"],
            "modules": sorted({e["path"].split("/")[1] for e in entries if e["path"].startswith("modules/") and len(e["path"].split("/")) > 1}),
        },
    }

    out.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"Wrote {out} (files={len(entries)})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""
ZOOP_METABLOOMS.py
Creates a ZOOP ledger event + receipt for this extracted bundle.

"ZOOP" = the act of extracting the external packaged artifact into a local filesystem
so that boot can proceed with on-disk authority.

This script is intentionally small and deterministic.
"""
from __future__ import annotations
import json, os, uuid, hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER_DIR = ROOT / "ledger"
LEDGER_PATH = LEDGER_DIR / "ledger.ndjson"
RECEIPT_PATH = LEDGER_DIR / "zoop_receipt.json"

def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _bundle_fingerprint() -> str:
    """
    Deterministic fingerprint of the extracted bundle root.
    This is NOT a substitute for ZIP hash; it's a guard against silent edits post-zoop.
    """
    boot = ROOT / "BOOT_METABLOOMS.py"
    manifest = ROOT / "boot_manifest.json"
    boot_md = ROOT / "BOOT.md"
    h = hashlib.sha256()
    for p in (boot_md, manifest, boot):
        h.update(p.name.encode("utf-8"))
        h.update(_sha256_file(p).encode("utf-8"))
    return h.hexdigest()

def main() -> int:
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    event_id = str(uuid.uuid4())
    ts = _now()
    fingerprint = _bundle_fingerprint()

    event = {
        "event_id": event_id,
        "ts": ts,
        "event_type": "ZOOP",
        "actor": "system",
        "artifact": {
            "name": "extracted_bundle_root",
            "sha256": fingerprint,
            "path": str(ROOT)
        },
        "meta": {
            "meaning": "ZOOP logged: external packaged artifact extracted to on-disk authority",
        }
    }

    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    receipt = {
        "zoop_event_id": event_id,
        "ts": ts,
        "artifact_name": "extracted_bundle_root",
        "artifact_sha256": fingerprint,
        "root_path": str(ROOT),
        "notes": "Receipt written by ZOOP_METABLOOMS.py"
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print("ZOOP_OK")
    print(f"zoop_event_id={event_id}")
    print(f"fingerprint_sha256={fingerprint}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

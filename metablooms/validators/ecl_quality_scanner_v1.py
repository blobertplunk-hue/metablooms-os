#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS.ECL
# ECL_RESPONSIBILITY: Deterministically measure ECL semantic quality (generic vs specific) without modifying files.

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

GENERIC_RESP = "Deterministic, truthful behavior; no hidden side effects; evidence-first."

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def scan_repo(root: Path) -> Dict:
    py_files: List[Path] = list(root.rglob("*.py"))
    by_scope: Dict[str, int] = {}
    generic: List[str] = []
    specific: List[str] = []
    files = []

    for p in py_files:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        scope = "UNKNOWN"
        resp = ""
        for line in txt.splitlines()[:120]:
            if line.strip().startswith("# ECL_SCOPE:"):
                scope = line.split(":", 1)[1].strip()
            if line.strip().startswith("# ECL_RESPONSIBILITY:"):
                resp = line.split(":", 1)[1].strip()

        by_scope[scope] = by_scope.get(scope, 0) + 1
        rel = str(p.relative_to(root))
        files.append({"path": rel, "scope": scope, "responsibility": resp})

        if resp == GENERIC_RESP:
            generic.append(rel)
        else:
            specific.append(rel)

    return {
        "schema": "ECL_QUALITY_SCAN_RESULT_V1",
        "ts_utc": now_iso(),
        "totals": {"py_files": len(py_files)},
        "generic_responsibility": generic,
        "specific_responsibility": specific,
        "by_scope": by_scope,
        "files": files
    }

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Measure ECL semantic quality (generic vs specific).")
    ap.add_argument("--root", default=".", help="Repo root")
    ap.add_argument("--out", default="ecl_quality_scan.json", help="Output JSON path")
    a = ap.parse_args()

    result = scan_repo(Path(a.root).resolve())
    Path(a.out).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"written": a.out, "py_files": result["totals"]["py_files"]}, sort_keys=True))

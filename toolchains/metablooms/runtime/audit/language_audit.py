# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Language Drift Audit Hook
Scans a directory tree for forbidden governance phrases that imply authority drift.

Fail-closed:
- Any forbidden phrase occurrence => FAIL (exit 2)

Default forbidden phrases are conservative and can be extended in a config file.

Usage:
python -m metablooms.runtime.audit.language_audit --root .
"""

import argparse
import json
import re
from pathlib import Path

DEFAULT_FORBIDDEN = [
    # Authority drift terms (module claims OS/boot authority)
    r"\bOS-shaped\b",
    r"\bnew OS\b",
    r"\bparallel OS\b",
    r"\bbootable system\b",
    r"\bRuntime active\b",
    r"\bBOOT_OK\b",
]

DEFAULT_FILE_GLOBS = ["**/*.md", "**/*.py", "**/*.txt", "**/*.json"]

def load_config(config_path: Path | None):
    if not config_path:
        return {"forbidden": DEFAULT_FORBIDDEN, "globs": DEFAULT_FILE_GLOBS}
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    forbidden = cfg.get("forbidden", DEFAULT_FORBIDDEN)
    globs = cfg.get("globs", DEFAULT_FILE_GLOBS)
    return {"forbidden": forbidden, "globs": globs}

def scan(root: Path, forbidden_patterns: list[str], globs: list[str]):
    hits = []
    compiled = [(pat, re.compile(pat, re.IGNORECASE)) for pat in forbidden_patterns]
    for g in globs:
        for p in root.glob(g):
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for pat, rx in compiled:
                for m in rx.finditer(text):
                    # record small context window
                    start = max(0, m.start()-40)
                    end = min(len(text), m.end()+40)
                    hits.append({
                        "file": str(p),
                        "pattern": pat,
                        "match": m.group(0),
                        "context": text[start:end].replace("\n"," ")
                    })
    ok = len(hits) == 0
    return {"ok": ok, "hits": hits, "hit_count": len(hits)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--config", default=None)
    args = ap.parse_args()

    cfg = load_config(Path(args.config) if args.config else None)
    result = scan(Path(args.root), cfg["forbidden"], cfg["globs"])
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()

# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Boot Import Audit
Static scan of BOOT_METABLOOMS.py (or other specified file) to enforce the boot import allowlist.

Fail-closed:
- Any import outside allowlist => FAIL
- Any forbidden prefix import => FAIL

Usage:
python -m metablooms.runtime.audit.boot_import_audit --boot-path BOOT_METABLOOMS.py --allowlist metablooms/invariants/boot_import_allowlist.json
"""

import argparse
import ast
import json
from pathlib import Path

def parse_imports(py_path: Path):
    tree = ast.parse(py_path.read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return sorted(set(imports))

def audit(boot_path: Path, allowlist_path: Path):
    allow = json.loads(allowlist_path.read_text(encoding="utf-8"))["allow"]
    deny = json.loads(allowlist_path.read_text(encoding="utf-8"))["deny"]

    allowed_std = set(allow.get("python_modules", []))
    allowed_mb = set(allow.get("metablooms_modules", []))
    denied_prefixes = tuple(deny.get("metablooms_modules_prefixes", []))

    imports = parse_imports(boot_path)

    violations = []
    for imp in imports:
        # treat metablooms.* as internal
        if imp.startswith("metblooms."):
            # (typo guard) treat as violation
            violations.append({"import": imp, "reason": "UNKNOWN_INTERNAL_PREFIX"})
            continue
        if imp.startswith("metablooms."):
            if imp in allowed_mb:
                continue
            if imp.startswith(denied_prefixes):
                violations.append({"import": imp, "reason": "DENIED_PREFIX"})
                continue
            violations.append({"import": imp, "reason": "NOT_IN_ALLOWLIST"})
            continue
        # stdlib (best-effort) — allow only listed to keep boot narrow
        root_mod = imp.split(".")[0]
        if root_mod not in allowed_std:
            violations.append({"import": imp, "reason": "STDLIB_NOT_IN_ALLOWLIST"})
    ok = len(violations) == 0
    return {"ok": ok, "imports": imports, "violations": violations}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot-path", required=True)
    ap.add_argument("--allowlist", required=True)
    args = ap.parse_args()

    result = audit(Path(args.boot_path), Path(args.allowlist))
    print(json.dumps(result, indent=2))
    if not result["ok"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()

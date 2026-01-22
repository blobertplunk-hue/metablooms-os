"""metablooms.tools.mb_apply_delta_failclosed

Fail-closed delta applier with P0 protected-path semantics.

Usage:
  python -m metablooms.tools.mb_apply_delta_failclosed --base <dir> --delta <zip> --out-ledger <jsonl>

Behavior:
- Applies added/modified files from DELTA_MANIFEST.json and zip members.
- If a protected path would be modified:
  - Checks semantic invariants (ECL headers + governance anchors)
  - If violation: STOP and ledger decision point.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List
import hashlib
import zipfile

from metablooms.invariants.p0_protect_boot_wiring import is_protected, evaluate_boot_entrypoint_semantics


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def append_ledger(path: Path, entry: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="Base directory to apply onto")
    ap.add_argument("--delta", required=True, help="Delta ZIP containing DELTA_MANIFEST.json + files")
    ap.add_argument("--out-ledger", required=True, help="JSONL ledger file to append to")
    args = ap.parse_args()

    base_dir = Path(args.base).resolve()
    delta_zip = Path(args.delta).resolve()
    ledger_path = Path(args.out_ledger).resolve()

    if not base_dir.exists():
        print(f"BASE_NOT_FOUND:{base_dir}", file=sys.stderr)
        return 2
    if not delta_zip.exists():
        print(f"DELTA_NOT_FOUND:{delta_zip}", file=sys.stderr)
        return 2

    with zipfile.ZipFile(delta_zip, "r") as z:
        if "DELTA_MANIFEST.json" not in z.namelist():
            print("DELTA_INVALID:NO_MANIFEST", file=sys.stderr)
            return 2
        manifest = json.loads(z.read("DELTA_MANIFEST.json").decode("utf-8"))
        members = [m for m in z.namelist() if m != "DELTA_MANIFEST.json"]

        for m in members:
            payload = z.read(m)
            target = base_dir / m
            target_rel = m.replace('\\', '/')

            # Protected path checks
            if is_protected(target_rel) and target.exists():
                proposed_text = payload.decode("utf-8", errors="replace")
                chk = evaluate_boot_entrypoint_semantics(proposed_text)
                if not chk.ok:
                    append_ledger(ledger_path, {
                        "event": "P0_BLOCK_PROTECTED_PATH",
                        "path": target_rel,
                        "delta": str(delta_zip.name),
                        "reasons": chk.reasons,
                        "canonical_sha256": sha256_bytes(target.read_bytes()),
                        "proposed_sha256": sha256_bytes(payload),
                        "decision_required": "KEEP_CANONICAL_OR_PROVIDE_ALLOWLISTED_PATCH",
                    })
                    print(f"P0_BLOCK_PROTECTED_PATH:{target_rel}:{','.join(chk.reasons)}", file=sys.stderr)
                    return 3  # governance-style block

            # Normal apply (fail-closed on mismatch if file exists and differs but not protected)
            if target.exists():
                if target.read_bytes() != payload:
                    # record but stop to preserve auditability
                    append_ledger(ledger_path, {
                        "event": "CONFLICT_CONTENT_MISMATCH",
                        "path": target_rel,
                        "delta": str(delta_zip.name),
                        "canonical_sha256": sha256_bytes(target.read_bytes()),
                        "proposed_sha256": sha256_bytes(payload),
                    })
                    print(f"CONFLICT_CONTENT_MISMATCH:{target_rel}", file=sys.stderr)
                    return 3

            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(payload)

            append_ledger(ledger_path, {
                "event": "APPLIED_FILE",
                "path": target_rel,
                "delta": str(delta_zip.name),
                "sha256": sha256_bytes(payload),
                "size": len(payload),
            })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

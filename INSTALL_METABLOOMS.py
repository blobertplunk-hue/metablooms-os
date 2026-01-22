#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: BOOTSTRAP.INSTALL
# ECL_RESPONSIBILITY: Validate byte-truth and run declared preflight; emit ledger evidence; no overclaim.

import argparse, json, sys
from pathlib import Path
from datetime import datetime, timezone
import subprocess

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def ledger_append(path: Path, obj: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj, sort_keys=True) + "\n")

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--os-root", default=".")
    ap.add_argument("--ledger", default="ledger.ndjson")
    ap.add_argument("--chain", default="metablooms/registry/preflight_gate_chain_v1.json")
    ap.add_argument("--preflight", default="metablooms/preflight/preflight_runner.py")
    a = ap.parse_args()

    root = Path(a.os_root).resolve()
    ledger = Path(a.ledger).resolve()

    boot = root / "BOOT_METABLOOMS.py"
    if not boot.exists():
        ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_BLOCK", "status": "BLOCK", "reason": "missing BOOT_METABLOOMS.py", "os_root": str(root)})
        print("BLOCK: missing BOOT_METABLOOMS.py")
        return 2

    chain = root / a.chain
    if not chain.exists():
        ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_BLOCK", "status": "BLOCK", "reason": "missing gate chain", "chain": str(chain)})
        print("BLOCK: missing gate chain")
        return 2

    ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_START", "status": "OK", "os_root": str(root), "chain": str(chain)})

    preflight = root / a.preflight
    if preflight.exists():
        cmd = [sys.executable, str(preflight), "--chain", str(chain), "--ledger", str(ledger)]
        ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_RUN", "status": "OK", "cmd": cmd})
        proc = subprocess.run(cmd, cwd=str(root))
        ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_DONE", "status": "OK" if proc.returncode == 0 else "BLOCK", "returncode": proc.returncode})
        return proc.returncode
    else:
        cmd = [sys.executable, str(boot)]
        ledger_append(ledger, {"ts": now_iso(), "event": "INSTALL_FALLBACK_BOOT", "status": "WARN", "cmd": cmd})
        proc = subprocess.run(cmd, cwd=str(root))
        return proc.returncode

if __name__ == "__main__":
    raise SystemExit(main())

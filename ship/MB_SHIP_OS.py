# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms OS Shipping Pipeline (P0)
This script is included to make the shipping procedure auditable and repeatable.
It is intentionally conservative and fail-closed.
"""

from __future__ import annotations
import re, json, zipfile, hashlib, shutil, subprocess, sys
from pathlib import Path
from dataclasses import dataclass

SEMVER_RE = re.compile(r"v(\d+)\.(\d+)\.(\d+)")

@dataclass(frozen=True)
class ShipResult:
    status: str
    baseline_zip: str | None = None
    output_zip: str | None = None
    reason: str | None = None

def _parse_semver(name: str):
    m = SEMVER_RE.search(name)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())

def resolve_baseline(search_dir: Path) -> Path | None:
    zips = list(search_dir.glob("*.zip"))
    candidates = []
    for z in zips:
        if "MetaBlooms_OS" not in z.name:
            continue
        if ("FULL" not in z.name) and ("WITH" not in z.name):
            continue
        ver = _parse_semver(z.name)
        if ver is None:
            continue
        candidates.append((ver, z.stat().st_size, z))
    if not candidates:
        return None
    candidates.sort(reverse=True)
    # Highest semver wins; size is only informative.
    return candidates[0][2]

def validate_baseline(zip_path: Path) -> tuple[bool, str]:
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            names = set(z.namelist())
            if "BOOT.md" not in names and "boot_manifest.json" not in names:
                return False, "missing_boot_markers"
            # Try typical entrypoints; allow variants.
            entrypoints = [n for n in names if n.endswith("BOOT_METABLOOMS.py") or n.endswith("RUN_METABLOOMS.py") or n.endswith("BOOT.md")]
            if not entrypoints:
                return False, "missing_entrypoint_like_files"
    except Exception as e:
        return False, f"zip_read_error:{e}"
    return True, "ok"

def build_inventory_sha256(root: Path) -> dict:
    inv = {}
    for p in root.rglob("*"):
        if p.is_file():
            rel = str(p.relative_to(root))
            h = hashlib.sha256(p.read_bytes()).hexdigest()
            inv[rel] = h
    return inv

def ship(search_dir: Path, deltas_root: Path, output_zip: Path) -> ShipResult:
    baseline = resolve_baseline(search_dir)
    if baseline is None:
        return ShipResult(status="SHIP_FAILED", reason="no_canonical_baseline")

    ok, why = validate_baseline(baseline)
    if not ok:
        return ShipResult(status="SHIP_FAILED", baseline_zip=str(baseline), reason=f"invalid_baseline:{why}")

    tmp = search_dir/"__ship_tmp_extract__"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)

    with zipfile.ZipFile(baseline, "r") as z:
        z.extractall(tmp)

    # Apply deltas: copy everything from deltas_root into tmp, overwriting where intended.
    for p in deltas_root.rglob("*"):
        if p.is_file():
            dest = tmp / p.relative_to(deltas_root)
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(p.read_bytes())

    # BOOT REQUIRED (P0): the staged tree must pass BOOT_METABLOOMS.py before we are allowed to ship.
    boot_py = tmp / "BOOT_METABLOOMS.py"
    if boot_py.exists():
        try:
            proc = subprocess.run(
                [sys.executable, str(boot_py)],
                cwd=str(tmp),
                capture_output=True,
                text=True,
                timeout=120,
            )
            # BOOT_METABLOOMS.py prints a JSON summary to stdout.
            boot_ok = False
            boot_status = None
            try:
                import json as _json
                boot_summary = _json.loads((proc.stdout or "").strip() or "{}")
                boot_status = boot_summary.get("status")
                boot_ok = (boot_status == "BOOT_OK")
            except Exception:
                boot_ok = False

            if (proc.returncode != 0) or (not boot_ok):
                return ShipResult(
                    status="SHIP_FAILED",
                    baseline_zip=str(baseline),
                    reason=f"boot_required_failed:rc={proc.returncode}:status={boot_status}:stdout={proc.stdout[-500:]}:stderr={proc.stderr[-500:]}"
                )
        except Exception as e:
            return ShipResult(status="SHIP_FAILED", baseline_zip=str(baseline), reason=f"boot_required_exception:{e}")
    else:
        return ShipResult(status="SHIP_FAILED", baseline_zip=str(baseline), reason="boot_required_missing_entrypoint")


    inv = build_inventory_sha256(tmp)
    (tmp/"INVENTORY_SHA256.json").write_text(json.dumps(inv, indent=2))

    # Zip
    with zipfile.ZipFile(output_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in tmp.rglob("*"):
            if p.is_file():
                z.write(p, p.relative_to(tmp))

    return ShipResult(status="SHIP_OK", baseline_zip=str(baseline), output_zip=str(output_zip))

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = here.parent
    out = root/"__SHIPPED_OS.zip"
    res = ship(search_dir=root, deltas_root=root/"__DELTAS__", output_zip=out)
    print(res)

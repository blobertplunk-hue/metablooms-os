
from pathlib import Path
import json

def prune_deltas(os_root: Path, keep_last: int = 50) -> list[Path]:
    deltas = os_root / "metablooms" / "state" / "deltas"
    if not deltas.exists():
        return []
    files = sorted([p for p in deltas.iterdir() if p.is_file()], key=lambda p: p.stat().st_mtime)
    removed = []
    if len(files) > keep_last:
        for p in files[:-keep_last]:
            p.unlink(missing_ok=True)
            removed.append(p)
    return removed

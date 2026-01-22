# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
import re, json

@dataclass
class DeltaIntent:
    source_path: str
    title: str
    targets: list[str]
    adds: list[str]
    notes: list[str]

def parse_delta_md(path: Path) -> DeltaIntent:
    txt = path.read_text(encoding="utf-8", errors="replace")
    title = (re.findall(r'^#\s+(.+)$', txt, flags=re.M) or [path.name])[0].strip()
    # naive target extraction: lines containing "MetaBlooms" or "OS" or "module"
    targets = sorted(set(re.findall(r'\b(?:module|modules|OS|MetaBlooms|SkillsFactory|Claude\s*Skills\s*Factory)\b.*', txt, flags=re.I)))
    adds = sorted(set(re.findall(r'\bADD\b.*|\bcreate\b.*|\bintroduce\b.*', txt, flags=re.I)))
    notes = []
    for ln in txt.splitlines():
        if ln.strip().startswith(("-", "*")) and len(ln) < 200:
            notes.append(ln.strip())
    return DeltaIntent(str(path), title, targets[:30], adds[:30], notes[:80])

def emit_receipt(intent: DeltaIntent, out_path: Path) -> None:
    out_path.write_text(json.dumps(asdict(intent), indent=2), encoding="utf-8")

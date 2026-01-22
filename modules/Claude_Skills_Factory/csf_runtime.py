# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json
from pathlib import Path

SKILL_REQUIRED_HEADINGS = ["Trigger", "Inputs", "Outputs"]

def discover_skills(root: Path) -> list[Path]:
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return []
    return [p for p in skills_dir.iterdir() if p.is_dir()]

def validate_skill(skill_dir: Path) -> dict:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"ok": False, "reason": "missing SKILL.md"}
    txt = skill_md.read_text(encoding="utf-8", errors="replace")
    missing = [h for h in SKILL_REQUIRED_HEADINGS if h not in txt]
    if missing:
        return {"ok": False, "reason": f"missing headings: {missing}"}
    # lightweight web.run/citation coupling
    if "web.run" in txt and "citation" not in txt.lower():
        return {"ok": False, "reason": "mentions web.run but not citations"}
    return {"ok": True}

def load_metadata(skill_dir: Path) -> dict:
    p = skill_dir / "metadata.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

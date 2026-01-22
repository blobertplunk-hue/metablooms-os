# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Gate: DOCS.HARDENING.FAIL_TO_FIX (v1)

P0 gate.

Behavior:
- Scan docs for forbidden terms (per CANONICAL_ONTOLOGY.md).
- If violations exist:
  - Apply Class A quarantine for historical/note/rebase/archive docs.
  - Apply Class B controlled rewrite for non-canonical docs (NOT ontology/literal specs).
- Re-scan.
- If still violating: fail-closed.

This gate performs *repair then validate*. It never allowlists.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional
from pathlib import Path
import re

from metablooms.validators.mb_validate_docs_forbidden_terms_v1 import validate_docs_forbidden_terms

GATE_ID = "GATE.P0.DOCS.HARDENING.FAIL_TO_FIX.V1"
P0 = True


def _is_class_a_quarantinable(p: Path) -> bool:
    name = p.name.lower()
    return any(k in name for k in ["note", "rebase", "archive", "history"]) or ("_note_" in name)


def _is_never_rewrite(p: Path, root: Path) -> bool:
    rel = p.relative_to(root).as_posix()
    if rel in ["docs/CANONICAL_ONTOLOGY.md", "docs/ARCHITECTURE_LITERAL.md", "docs/METAPHOR_LAYER.md", "docs/INTERPRETATION_CONTRACT.md"]:
        return True
    # Never rewrite code
    if rel.startswith("metablooms/") and rel.endswith(".py"):
        return True
    return False


def _class_b_rewrite(p: Path, forbidden_terms: list[str], replacements: dict[str, str]) -> bool:
    """Returns True if file changed."""
    text = p.read_text(encoding="utf-8", errors="replace")
    original = text

    changed = False
    for term in forbidden_terms:
        if term in text:
            repl = replacements.get(term)
            if repl:
                text = text.replace(term, repl)
                changed = True

    if changed:
        header = "<!-- AUTO_REWRITE_CLASS_B: MetaBlooms fail-to-fix applied; see ledgers/auto_repairs.jsonl -->\n"
        if not text.lstrip().startswith("<!-- AUTO_REWRITE_CLASS_B"):
            text = header + text
        p.write_text(text, encoding="utf-8")

    return changed and (text != original)


def run_gate(context: Dict[str, Any], ledger_writer: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
    root = Path(context.get("root") or context.get("os_root") or context.get("zroot") or ".").resolve()

    # First scan
    res1 = validate_docs_forbidden_terms(str(root))

    repairs = []

    # Deterministic replacements (Class B)
    # Keep this minimal and ontology-aligned.
    replacements = {
        "Kernel": "Canonical Runtime Discipline",
        "Cognitive Stack": "Pipeline-Oriented Transformation Layer",
        "Supervisor": "Detector/Gate",
        "Self-governing": "Governance-enforced",
        "Autonomous": "Externally constrained",
    }

    if not res1.ok:
        for f in res1.findings:
            p = Path(f.path)
            # Class A quarantine
            if _is_class_a_quarantinable(p):
                hist_dir = root / "docs/_historical"
                hist_dir.mkdir(parents=True, exist_ok=True)
                dest = hist_dir / p.name
                p.replace(dest)
                repairs.append({"action": "QUARANTINE", "from": str(p), "to": str(dest), "term": f.term})
                continue

            # Class B rewrite (controlled)
            if _is_never_rewrite(p, root):
                repairs.append({"action": "ESCALATE", "file": str(p), "term": f.term, "reason": "never_rewrite"})
                continue

            changed = _class_b_rewrite(p, res1.forbidden_terms, replacements)
            if changed:
                repairs.append({"action": "REWRITE_CLASS_B", "file": str(p), "term": f.term})
            else:
                repairs.append({"action": "ESCALATE", "file": str(p), "term": f.term, "reason": "no_replacement"})

    # Re-scan
    res2 = validate_docs_forbidden_terms(str(root))

    errors = [f"{ff.path}:{ff.line}:FORBIDDEN_TERM:{ff.term}:{ff.excerpt}" for ff in res2.findings]

    out = {
        "gate_id": GATE_ID,
        "p0": P0,
        "ok": res2.ok,
        "errors": errors,
        "repairs": repairs,
        "mode_active": True,
        "bypass_used": False,
    }

    if ledger_writer is not None:
        ledger_writer({
            "event_type": "DOCS_FAIL_TO_FIX_RESULT",
            "gate_id": GATE_ID,
            "ok": res2.ok,
            "repairs": repairs,
            "errors": errors,
        })

    return out

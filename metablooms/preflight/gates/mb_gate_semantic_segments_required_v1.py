# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""GATE.SEMANTIC.SEGMENTS.REQUIRED.V1

Ensures the semantic segments registry exists and validates.
Mode:
- Default WARN during boot to avoid breaking legacy pipelines.
- FAIL during SHIP (export) to enforce systemic adoption.

This gate does not yet require every pipeline section to declare segment_id;
that is introduced via separate schema migration. It enforces the registry
and establishes the enforcement hook.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from metablooms.validators.mb_validate_semantic_segments_v1 import validate_registry

GATE_ID = "GATE.SEMANTIC.SEGMENTS.REQUIRED.V1"

@dataclass
class GateOutcome:
    ok: bool
    gate_id: str
    level: str
    mode: str
    detail: str
    evidence: dict


def run_gate(run_context: dict) -> GateOutcome:
    mb_root = Path(run_context.get('mb_root', '.')).resolve()
    reg_path = mb_root / 'metablooms' / 'registry' / 'semantic_segments_v1.json'

    # Determine enforcement mode
    action = (run_context.get('mb_action') or run_context.get('action') or '').upper()
    requested_mode = (run_context.get('mb_semantic_segments_mode') or '').upper()

    if requested_mode in {'FAIL','WARN'}:
        mode = requested_mode
    else:
        mode = 'FAIL' if action in {'SHIP','EXPORT','PUBLISH'} else 'WARN'

    res = validate_registry(reg_path)

    if res.ok:
        return GateOutcome(True, GATE_ID, 'P1', mode, 'Semantic segments registry valid.', {
            'registry_path': str(reg_path)
        })

    detail = 'Semantic segments registry invalid: ' + ';'.join(res.errors)
    ok = (mode != 'FAIL')
    return GateOutcome(ok, GATE_ID, 'P1', mode, detail, {
        'registry_path': str(reg_path),
        'errors': res.errors,
        'action': action or None
    })

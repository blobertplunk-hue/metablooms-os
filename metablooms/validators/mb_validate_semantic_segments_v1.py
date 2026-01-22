# ECL_VERSION: 1
# ECL_SCOPE: VALIDATORS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""MetaBlooms Semantic Segments Validator v1.

Validates the semantic segments registry (structure + invariants).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re

SEG_ID_RE = re.compile(r'^seg\.[a-z0-9_]+(\.[a-z0-9_]+)*\.v[0-9]+$')

REQUIRED_TOP = ['version','registry_id','authority','llm_roles','segments']
REQUIRED_SEG = ['segment_id','intent','required_inputs','produces','allowed_ops','forbidden_ops','validators','evidence_requirements','llm_role','constraints_ref']

@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding='utf-8'))

def validate_registry(reg_path: str | Path) -> ValidationResult:
    reg_path = Path(reg_path)
    errors: list[str] = []
    if not reg_path.exists():
        return ValidationResult(False, [f'missing:{reg_path}'])
    try:
        data = load_json(reg_path)
    except Exception as e:
        return ValidationResult(False, [f'json_parse_error:{e}'])
    for k in REQUIRED_TOP:
        if k not in data:
            errors.append(f'missing_key:{k}')
    segs = data.get('segments', [])
    if not isinstance(segs, list) or len(segs) == 0:
        errors.append('segments_must_be_nonempty_list')
        return ValidationResult(False, errors)
    seen=set()
    for i,s in enumerate(segs):
        if not isinstance(s, dict):
            errors.append(f'segment_{i}_not_object')
            continue
        for k in REQUIRED_SEG:
            if k not in s:
                errors.append(f'segment_{i}_missing:{k}')
        sid = s.get('segment_id','')
        if not isinstance(sid,str) or not SEG_ID_RE.match(sid):
            errors.append(f'segment_{i}_bad_id:{sid}')
        if sid in seen:
            errors.append(f'duplicate_segment_id:{sid}')
        seen.add(sid)
        role = s.get('llm_role')
        if role and role not in set(data.get('llm_roles', [])):
            errors.append(f'segment_{i}_invalid_llm_role:{role}')
    return ValidationResult(len(errors)==0, errors)

def validate_or_raise(reg_path: str | Path) -> None:
    res = validate_registry(reg_path)
    if not res.ok:
        raise ValueError('SEMANTIC_SEGMENTS_INVALID:' + ';'.join(res.errors))

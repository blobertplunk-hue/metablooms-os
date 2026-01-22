# ECL_VERSION: 1
# ECL_SCOPE: PREFLIGHT.GATES
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""GATE.SEMANTIC.SEGMENTS.COVERAGE.V1

Computes a coarse coverage score for semantic segments across pipeline specs.

Purpose
- Encourage systemic use of semantic segments without breaking legacy immediately.

Method
- Scan `pipelines/**/*.pipeline.yaml` for `segment_id:` tokens.
- Coverage = (# pipeline specs containing at least one segment_id) / (total pipeline specs)

Enforcement
- During BOOT: WARN only.
- During SHIP/EXPORT: FAIL if coverage < threshold.

Threshold default: 80% (configurable via run_context)
"""

from __future__ import annotations

from pathlib import Path

GATE_ID = "GATE.SEMANTIC.SEGMENTS.COVERAGE.V1"


def run_gate(run_context: dict) -> dict:
    mb_root = Path(run_context.get('mb_root', '.')).resolve()
    pipelines_dir = mb_root / 'pipelines'

    action = (run_context.get('mb_action') or run_context.get('action') or '').upper()
    threshold = float(run_context.get('mb_semantic_segments_coverage_threshold', 80))

    specs = list(pipelines_dir.rglob('*.pipeline.yaml')) if pipelines_dir.exists() else []
    total = len(specs)
    with_seg = 0
    missing = []

    for p in specs:
        try:
            txt = p.read_text(encoding='utf-8', errors='replace')
        except Exception:
            txt = ''
        if 'segment_id:' in txt:
            with_seg += 1
        else:
            missing.append(str(p.relative_to(mb_root)))

    coverage = 100.0 if total == 0 else (with_seg / total) * 100.0

    # default behavior: warn on boot, fail on ship when below threshold
    mode = 'FAIL' if action in {'SHIP','EXPORT','PUBLISH'} else 'WARN'
    ok = True if mode == 'WARN' else (coverage >= threshold)

    detail = f"coverage={coverage:.1f}% ({with_seg}/{total}) threshold={threshold:.1f}%"

    return {
        'gate_id': GATE_ID,
        'ok': ok,
        'level': 'P1',
        'mode': mode,
        'detail': detail,
        'coverage_percent': coverage,
        'missing_segment_id_specs': missing[:50],
        'total_specs': total,
    }

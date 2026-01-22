"""Receipt metrics (v1).

Optional utility to summarize SEE receipts stored under an evidence root.

This module is intentionally read-only and does not participate in gating by default.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Any, List


def load_receipts(evidence_root: str) -> List[Dict[str, Any]]:
    receipts: List[Dict[str, Any]] = []
    for root, _, files in os.walk(evidence_root):
        for fn in files:
            if fn.endswith('.receipt.json'):
                path = os.path.join(root, fn)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        receipts.append(json.load(f))
                except Exception:
                    # Best-effort: observability must not break core workflows.
                    continue
    return receipts


def summarize_receipts(receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(receipts)
    by_exit: Dict[str, int] = {}
    by_level: Dict[str, int] = {}
    durations: List[int] = []

    for r in receipts:
        exit_code = str(((r.get('exec') or {}).get('exit_code')))
        by_exit[exit_code] = by_exit.get(exit_code, 0) + 1

        level = str(r.get('evidence_level_claimed'))
        by_level[level] = by_level.get(level, 0) + 1

        dur = (r.get('exec') or {}).get('duration_ms')
        if isinstance(dur, int):
            durations.append(dur)

    durations.sort()
    p50 = durations[len(durations)//2] if durations else None
    p95 = durations[int(len(durations)*0.95)] if durations else None

    return {
        'total_receipts': total,
        'by_exit_code': by_exit,
        'by_evidence_level': by_level,
        'duration_ms_p50': p50,
        'duration_ms_p95': p95,
    }

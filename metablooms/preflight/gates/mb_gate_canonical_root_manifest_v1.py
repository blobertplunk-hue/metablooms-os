"""metablooms.preflight.gates.mb_gate_canonical_root_manifest_v1

P0 gate: Canonical Root Manifest must exist and match the immutable boot entrypoint.

Checks:
- metablooms/runtime/canonical_root.json exists
- required_paths listed in manifest exist
- BOOT_METABLOOMS.py SHA256 matches manifest

Fail-closed: any mismatch fails the preflight.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run_gate(run_ctx: Dict[str, Any]) -> Dict[str, Any]:
    """Return a standard MetaBlooms gate result dict."""
    root = Path(run_ctx.get('zroot', '.')).resolve()
    manifest_path = root / 'metablooms' / 'runtime' / 'canonical_root.json'

    if not manifest_path.exists():
        return {
            'pass': False,
            'gate': 'GATE.P0.CANONICAL.ROOT.MANIFEST.V1',
            'reason': 'CANONICAL_ROOT_MANIFEST_MISSING',
            'expected': str(manifest_path),
        }

    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    except Exception as e:
        return {
            'pass': False,
            'gate': 'GATE.P0.CANONICAL.ROOT.MANIFEST.V1',
            'reason': 'CANONICAL_ROOT_MANIFEST_UNREADABLE',
            'error': repr(e),
            'path': str(manifest_path),
        }

    required_paths = manifest.get('required_paths', [])
    missing = []
    for rp in required_paths:
        p = root / rp
        if not p.exists():
            missing.append(rp)

    if missing:
        return {
            'pass': False,
            'gate': 'GATE.P0.CANONICAL.ROOT.MANIFEST.V1',
            'reason': 'CANONICAL_ROOT_REQUIRED_PATHS_MISSING',
            'missing_paths': missing,
        }

    boot_rel = manifest.get('boot_entrypoint', 'BOOT_METABLOOMS.py')
    boot_path = root / boot_rel
    boot_sha = _sha256_file(boot_path)
    expected_sha = manifest.get('boot_entrypoint_sha256')

    if expected_sha and boot_sha != expected_sha:
        return {
            'pass': False,
            'gate': 'GATE.P0.CANONICAL.ROOT.MANIFEST.V1',
            'reason': 'BOOT_ENTRYPOINT_SHA256_MISMATCH',
            'expected_sha256': expected_sha,
            'actual_sha256': boot_sha,
            'entrypoint': boot_rel,
        }

    return {
        'pass': True,
        'gate': 'GATE.P0.CANONICAL.ROOT.MANIFEST.V1',
        'canonical_zip_basename': manifest.get('canonical_zip_basename'),
        'boot_entrypoint': boot_rel,
        'boot_entrypoint_sha256': boot_sha,
    }

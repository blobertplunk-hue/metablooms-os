# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# runtime/tools/artifact2_preflight.py
# Deterministic member filter for Artifact 2 ZIP (exclude __MACOSX/ and ._ sidecars; exclude tiny files).
import json, zipfile
from pathlib import Path

def is_macos_sidecar(path: str) -> bool:
    p = path.replace('\\','/')
    name = p.split('/')[-1]
    return p.startswith('__MACOSX/') or name.startswith('._')

def preflight(zip_path: str, min_bytes: int = 200):
    zp = Path(zip_path)
    assert zp.exists(), f"Missing ZIP: {zip_path}"
    with zipfile.ZipFile(zp,'r') as z:
        members = sorted([m for m in z.namelist() if m.lower().endswith('.jsonl')])
        excluded=[]
        included=[]
        for m in members:
            reason=None
            if is_macos_sidecar(m):
                reason='MACOS_SIDECAR'
            else:
                sz=z.getinfo(m).file_size
                if sz < min_bytes:
                    reason='TINY_OR_EMPTY'
            if reason:
                excluded.append({'member_path': m, 'reason': reason, 'bytes': z.getinfo(m).file_size})
            else:
                included.append(m)
    return {'members_all': members, 'included': included, 'excluded': excluded}

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("usage: python artifact2_preflight.py <path_to_artifact2_zip>")
        raise SystemExit(2)
    out = preflight(sys.argv[1])
    reasons = {r: sum(1 for e in out['excluded'] if e['reason']==r) for r in sorted({e['reason'] for e in out['excluded']})}
    print(json.dumps({'all': len(out['members_all']), 'included': len(out['included']), 'excluded': len(out['excluded']), 'excluded_by_reason': reasons}, indent=2))

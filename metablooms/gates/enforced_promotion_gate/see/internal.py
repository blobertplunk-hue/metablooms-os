import os
import hashlib

def _hash_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()

def _hash_path(path: str | None) -> str | None:
    if not path or not os.path.exists(path):
        return None
    if os.path.isdir(path):
        parts = []
        for root, _, files in os.walk(path):
            for fn in sorted(files):
                fp = os.path.join(root, fn)
                try:
                    st = os.stat(fp)
                    parts.append(f"{os.path.relpath(fp, path)}:{st.st_size}")
                except OSError:
                    parts.append(f"{os.path.relpath(fp, path)}:ERR")
        return _hash_bytes("\n".join(parts).encode("utf-8"))
    with open(path, "rb") as f:
        return _hash_bytes(f.read())

def see_internal(candidate_path: str, policy_path: str | None) -> dict:
    '''
    Internal SEE: capture minimal hashes and detect dependency semantics via marker file.
    Marker: if candidate or policy contains NEEDS_UPSTREAM_SEMANTICS, semantics are involved.
    '''
    cand_hash = _hash_path(candidate_path)
    pol_hash = _hash_path(policy_path)

    dependency = False
    for p in [candidate_path, policy_path]:
        if p and os.path.isdir(p):
            if os.path.exists(os.path.join(p, "NEEDS_UPSTREAM_SEMANTICS")):
                dependency = True

    return {
        "input_hashes": {
            "candidate_bundle": f"sha256:{cand_hash}" if cand_hash else None,
            "policy_bundle": f"sha256:{pol_hash}" if pol_hash else None
        },
        "dependency_semantics_detected": dependency
    }

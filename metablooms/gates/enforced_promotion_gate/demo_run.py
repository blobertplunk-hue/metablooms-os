import os
import json
import pathlib
import subprocess
import sys

def _write_external_item(path: str, item: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(item, f, indent=2)

def main():
    cand = "/mnt/data/demo_candidate_bundle"
    pol = "/mnt/data/demo_policy_bundle"
    os.makedirs(cand, exist_ok=True)
    os.makedirs(pol, exist_ok=True)
    pathlib.Path(os.path.join(cand, "NEEDS_UPSTREAM_SEMANTICS")).write_text("1", encoding="utf-8")

    evidence_root = "/mnt/data/metablooms_evidence"

    cmd1 = [sys.executable, "-m", "metablooms_gate.cli",
            "--candidate", cand,
            "--target", "CANONICAL",
            "--policy", pol,
            "--evidence-dir", evidence_root,
            "--run-id", "PROMOTION-2026-01-19-001"]
    r1 = subprocess.run(cmd1, capture_output=True, text=True)
    print("RUN1 exit:", r1.returncode)
    print(r1.stdout.strip())

    ext_dir = "/mnt/data/demo_external_items"
    os.makedirs(ext_dir, exist_ok=True)
    ext1 = os.path.join(ext_dir, "ext1.json")
    ext2 = os.path.join(ext_dir, "ext2.json")

    _write_external_item(ext1, {
        "item_id": "EXT-SEE-001",
        "source_type": "docs",
        "source_locator": {"canonical": "https://example.org/tool/docs/enforcement"},
        "retrieved_at": "2026-01-19T14:55:00Z",
        "collector": {"agent": "SEE", "method": "manual_entry"},
        "capture": {"kind": "summary", "body": "Upstream docs describe enforcement semantics.", "byte_len": 52, "word_len": 6, "content_type": "text/plain"},
        "relevance_claim": {"supports": "enforcement semantics for tool", "applies_to": ["EXTERNAL_SEE_REQUIRED_FOR_PROMOTION"], "mdls_implicated": ["MDL-0003"]},
        "confidence": "HIGH",
        "content_hash": {"algo": "sha256", "value": "111aaa111aaa111aaa111aaa111aaa111aaa111aaa111aaa111aaa111aaa111a"}
    })
    _write_external_item(ext2, {
        "item_id": "EXT-SEE-002",
        "source_type": "issue",
        "source_locator": {"canonical": "https://example.org/tool/issues/123"},
        "retrieved_at": "2026-01-19T14:56:00Z",
        "collector": {"agent": "SEE", "method": "manual_entry"},
        "capture": {"kind": "summary", "body": "Issue confirms behavior in practice.", "byte_len": 34, "word_len": 6, "content_type": "text/plain"},
        "relevance_claim": {"supports": "corroboration of semantics", "applies_to": ["EXTERNAL_SEE_REQUIRED_FOR_PROMOTION"], "mdls_implicated": ["MDL-0003"]},
        "confidence": "MED",
        "content_hash": {"algo": "sha256", "value": "222bbb222bbb222bbb222bbb222bbb222bbb222bbb222bbb222bbb222bbb222b"}
    })

    cmd2 = [sys.executable, "-m", "metablooms_gate.cli",
            "--candidate", cand,
            "--target", "CANONICAL",
            "--policy", pol,
            "--evidence-dir", evidence_root,
            "--run-id", "PROMOTION-2026-01-19-002",
            "--parent-evidence-id", "sha256:9d3b8a9f0d8a4c2a1c5a0e2b4b9c7e8f1d2a3b4c5d6e7f8a9b0c1d2e3f4a",
            "--external-evidence", ext1,
            "--external-evidence", ext2]
    r2 = subprocess.run(cmd2, capture_output=True, text=True)
    print("RUN2 exit:", r2.returncode)
    print(r2.stdout.strip())

if __name__ == "__main__":
    main()

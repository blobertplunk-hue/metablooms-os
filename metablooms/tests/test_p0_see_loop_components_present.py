import os

def test_components_present():
    required = [
        "metablooms/loop/see_recursive_controller_v1.py",
        "metablooms/runtime/sandbox_exec_v1.py",
        "metablooms/evidence/store_v1.py",
        "metablooms/evidence/receipt_validate_v1.py",
        "metablooms/preflight/gates/mb_gate_evidence_see_loop_v1.py",
    ]
    for p in required:
        assert os.path.exists(p)

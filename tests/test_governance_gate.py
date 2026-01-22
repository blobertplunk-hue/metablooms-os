import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RUNTIME = os.path.join(ROOT, 'metablooms_runtime')
if RUNTIME not in sys.path:
    sys.path.insert(0, RUNTIME)

from gates.governance_gate import run_governance_gate, GovernanceBlock
from metablooms.loop.see_recursive_controller import SEEStopReason


def test_blocks_if_see_not_success():
    blocked = False
    try:
        run_governance_gate(
            see_stop_reason=SEEStopReason.EXECUTION_ERROR,
            mmd_inputs={"plan": None, "code_refs": [], "evidence_pointers": [], "gate_passed": True, "iteration": 1, "max_iterations": 2, "improved": True},
            ecl_inputs={"module_globals": {"ECL_VERSION": "1", "ECL_SCOPE": "T", "ECL_RESPONSIBILITY": "R"}, "claims": [], "evidence_pointers": [], "run_hashes": []},
        )
    except GovernanceBlock:
        blocked = True
    assert blocked


def test_blocks_if_mmd_blocks():
    blocked = False
    try:
        # plan exists, no code refs -> PLAN_CODE should BLOCK
        run_governance_gate(
            see_stop_reason=SEEStopReason.SUCCESS,
            mmd_inputs={"plan": {"steps": ["do x"]}, "code_refs": [], "evidence_pointers": [], "gate_passed": True, "iteration": 1, "max_iterations": 2, "improved": True},
            ecl_inputs={"module_globals": {"ECL_VERSION": "1", "ECL_SCOPE": "T", "ECL_RESPONSIBILITY": "R"}, "claims": [], "evidence_pointers": [], "run_hashes": []},
        )
    except GovernanceBlock:
        blocked = True
    assert blocked


def test_blocks_if_ecl_blocks():
    blocked = False
    try:
        # claims exist, no evidence -> ECL should BLOCK
        run_governance_gate(
            see_stop_reason=SEEStopReason.SUCCESS,
            mmd_inputs={"plan": None, "code_refs": [], "evidence_pointers": [], "gate_passed": True, "iteration": 1, "max_iterations": 2, "improved": True},
            ecl_inputs={"module_globals": {"ECL_VERSION": "1", "ECL_SCOPE": "T", "ECL_RESPONSIBILITY": "R"}, "claims": ["c1"], "evidence_pointers": [], "run_hashes": []},
        )
    except GovernanceBlock:
        blocked = True
    assert blocked


def test_passes_happy_path():
    run_governance_gate(
        see_stop_reason=SEEStopReason.SUCCESS,
        mmd_inputs={"plan": None, "code_refs": [], "evidence_pointers": [], "gate_passed": True, "iteration": 1, "max_iterations": 2, "improved": True},
        ecl_inputs={"module_globals": {"ECL_VERSION": "1", "ECL_SCOPE": "T", "ECL_RESPONSIBILITY": "R"}, "claims": [], "evidence_pointers": [], "run_hashes": ["abc"]},
    )

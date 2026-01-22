#!/usr/bin/env python3
# ECL_VERSION: 1
# ECL_SCOPE: TOOLS
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

"""tools/ci_gate_v1.py
Mandatory CI gate executed during BOOT.
Runs validators for stages: boot, post_boot.
Fail-closed by default. Legacy escape hatch: MB_ALLOW_LEGACY_VALIDATION=1
"""
from __future__ import annotations
import os
from validators.validator_runner_v1 import run_validators

def run_ci_gate() -> str:
    # boot validators
    run_validators(stage="boot")
    # post-boot validators
    run_validators(stage="post_boot")
    return "CI_GATE_OK"

if __name__ == "__main__":
    print(run_ci_gate())

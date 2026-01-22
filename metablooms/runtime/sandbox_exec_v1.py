import os
import platform
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

from metablooms.evidence.store_v1 import EvidenceStore


def sandbox_execute(task_spec: Dict[str, Any], iteration: int) -> Dict[str, Any]:
    """Execute a command with evidence capture.

    task_spec required keys:
      - artifact_id: str
      - command: List[str]
      - workdir: str
      - evidence_root: str
      - timeout_seconds: int (optional, default 30)

    Returns:
      - exit_code: int
      - timed_out: bool
      - stdout_path: str
      - stderr_path: str
      - receipt_path: str
    """
    artifact_id = str(task_spec.get("artifact_id") or task_spec.get("task_id") or "").strip()
    if not artifact_id:
        raise ValueError("task_spec.artifact_id (or task_id) required")

    command = task_spec.get("command")
    if not isinstance(command, list) or not all(isinstance(x, str) for x in command):
        raise ValueError("task_spec.command must be List[str]")

    workdir = str(task_spec.get("workdir") or ".")
    evidence_root = str(task_spec.get("evidence_root") or os.path.join("/mnt/data", "sandbox_runs"))
    timeout_seconds = int(task_spec.get("timeout_seconds") or 30)

    store = EvidenceStore(
        evidence_root,
        min_free_bytes=task_spec.get("min_free_bytes"),
        max_artifact_bytes=task_spec.get("max_artifact_bytes"),
        max_total_task_bytes=task_spec.get("max_total_task_bytes"),
    )
    attempt_dir = store.alloc_attempt_dir(artifact_id, iteration)

    stdout_path = os.path.join(attempt_dir, "stdout.txt")
    stderr_path = os.path.join(attempt_dir, "stderr.txt")

    started = time.time()
    timed_out = False
    exit_code = 1

    try:
        with open(stdout_path, "w", encoding="utf-8") as so, open(stderr_path, "w", encoding="utf-8") as se:
            try:
                proc = subprocess.run(
                    command,
                    cwd=workdir,
                    stdout=so,
                    stderr=se,
                    timeout=timeout_seconds,
                    check=False,
                )
                exit_code = int(proc.returncode)
            except subprocess.TimeoutExpired:
                timed_out = True
                exit_code = 124
            except Exception as e:  # noqa: BLE001
                # Fail-closed: capture error into stderr evidence.
                timed_out = False
                exit_code = 125
                try:
                    se.write(f"SANDBOX_EXEC_EXCEPTION:{type(e).__name__}:{e}\n")
                except Exception:
                    pass
    except Exception as e:  # noqa: BLE001
        # If we cannot even open evidence files, fail-closed with explicit error.
        raise ValueError(f"EVIDENCE_IO_FAILED:{type(e).__name__}:{e}")

    finished = time.time()

    # Evidence level heuristic:
    #   - E2 if nonzero exit
    #   - E3 if exit=0
    #   - E1 if timed_out (no determinism)
    if timed_out:
        evidence_level = "E1"
    else:
        evidence_level = "E3" if exit_code == 0 else "E2"

    artifacts = store.list_artifacts_with_hashes([stdout_path, stderr_path])

    receipt = {
        "receipt_version": "SEE_RECEIPT_V1",
        "artifact_id": artifact_id,
        "iteration": iteration,
        "command": command,
        "workdir": workdir,
        "exec": {
            "exit_code": exit_code,
            "timed_out": timed_out,
            "timeout_seconds": timeout_seconds,
            "duration_ms": int((finished - started) * 1000),
        },
        "artifacts": artifacts,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
        },
        "evidence_level_claimed": evidence_level,
    }

    receipt_path = store.write_receipt(attempt_dir, receipt)

    return {
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
        "receipt_path": receipt_path,
        "attempt_dir": attempt_dir,
        "evidence_level_claimed": evidence_level,
    }

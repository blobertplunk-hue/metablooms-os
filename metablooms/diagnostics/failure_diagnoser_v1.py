import os
from typing import Any, Dict


def _tail(path: str, n: int = 80) -> str:
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        return "".join(lines[-n:])
    except Exception:
        return ""


def diagnose(task_spec: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    """Evidence-based failure diagnosis.

    This is intentionally mechanical: it classifies by exit_code / timeout and provides
    stderr tail to inform patch providers.
    """
    exit_code = int(result.get("exit_code") or 1)
    timed_out = bool(result.get("timed_out"))
    stderr_tail = _tail(result.get("stderr_path"), n=120)

    if timed_out:
        rule = "TIMEOUT"
    elif exit_code == 0:
        rule = "SUCCESS"
    else:
        rule = "NONZERO_EXIT"

    return {
        "rule": rule,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stderr_tail": stderr_tail,
        "receipt_path": result.get("receipt_path"),
        "attempt_dir": result.get("attempt_dir"),
        "artifact_id": task_spec.get("artifact_id") or task_spec.get("task_id"),
    }

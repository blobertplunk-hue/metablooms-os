import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from metablooms.evidence.store_v1 import sha256_file


@dataclass
class RegressionResult:
    ok: bool
    reason: str
    details: Dict[str, Any]


class RegressionTracker:
    """Lightweight, deterministic regression tracker.

    Strategy:
      - after first PASS, capture baseline hashes for selected paths
      - on subsequent PASS, require hashes to match baseline

    This is intentionally conservative: it blocks silent drift for artifacts you care about.
    """

    def __init__(self, baseline_path: str, tracked_paths: Optional[List[str]] = None):
        self.baseline_path = baseline_path
        self.tracked_paths = tracked_paths or []

    def _signature(self) -> Dict[str, str]:
        sig: Dict[str, str] = {}
        for p in self.tracked_paths:
            if os.path.exists(p):
                sig[p] = sha256_file(p)
            else:
                sig[p] = "MISSING"
        return sig

    def capture_baseline(self) -> Dict[str, str]:
        sig = self._signature()
        os.makedirs(os.path.dirname(self.baseline_path), exist_ok=True)
        with open(self.baseline_path, "w", encoding="utf-8") as f:
            json.dump({"tracked_paths": self.tracked_paths, "sha256": sig}, f, indent=2, sort_keys=True)
        return sig

    def check(self) -> RegressionResult:
        if not os.path.exists(self.baseline_path):
            # No baseline yet; caller decides whether to capture.
            return RegressionResult(ok=True, reason="NO_BASELINE", details={})

        with open(self.baseline_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        baseline = data.get("sha256", {})
        current = self._signature()

        mismatches = {p: {"baseline": baseline.get(p), "current": current.get(p)} for p in current if baseline.get(p) != current.get(p)}
        if mismatches:
            return RegressionResult(ok=False, reason="REGRESSION_HASH_MISMATCH", details={"mismatches": mismatches})
        return RegressionResult(ok=True, reason="OK", details={})

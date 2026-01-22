import json
import os
from typing import Any, Dict, Set

import jsonschema

from metablooms.evidence.store_v1 import sha256_file

REQUIRED_FIELDS: Set[str] = {
    "receipt_version",
    "artifact_id",
    "iteration",
    "command",
    "workdir",
    "exec",
    "artifacts",
    "environment",
    "evidence_level_claimed",
}

ALLOWED_EVIDENCE = {"E0", "E1", "E2", "E3", "E4"}


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_receipt(receipt_path: str) -> None:
    """Fail-closed receipt validator.

    Validates:
      - file exists
      - required top-level fields present
      - artifacts exist and sha256 matches
    """
    if not os.path.exists(receipt_path):
        raise ValueError("RECEIPT_NOT_FOUND")

    data = _load_json(receipt_path)

    # Schema enforcement (fail-closed if schema present but validation fails).
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "schemas",
        "see_receipt_v1.schema.json",
    )
    if os.path.exists(schema_path):
        schema = _load_json(schema_path)
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"RECEIPT_SCHEMA_INVALID:{e.message}")
    missing = sorted(list(REQUIRED_FIELDS - set(data.keys())))
    if missing:
        raise ValueError(f"RECEIPT_MISSING_FIELDS:{missing}")

    if data.get("receipt_version") != "SEE_RECEIPT_V1":
        raise ValueError(f"RECEIPT_VERSION_INVALID:{data.get('receipt_version')}")

    if data.get("evidence_level_claimed") not in ALLOWED_EVIDENCE:
        raise ValueError(f"RECEIPT_INVALID_EVIDENCE_LEVEL:{data.get('evidence_level_claimed')}")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("RECEIPT_ARTIFACTS_NOT_LIST")

    for a in artifacts:
        if not isinstance(a, dict):
            raise ValueError("RECEIPT_ARTIFACT_ENTRY_NOT_OBJECT")
        p = a.get("path")
        h = a.get("sha256")
        if not isinstance(p, str) or not isinstance(h, str):
            raise ValueError("RECEIPT_ARTIFACT_ENTRY_MISSING_PATH_OR_HASH")
        if not os.path.exists(p):
            raise ValueError(f"ARTIFACT_NOT_FOUND:{p}")
        actual = sha256_file(p)
        if actual != h:
            raise ValueError(f"HASH_MISMATCH:{p}")


def require_evidence_at_least(receipt_path: str, required: str) -> None:
    order = {"E0": 0, "E1": 1, "E2": 2, "E3": 3, "E4": 4}
    data = _load_json(receipt_path)
    claimed = data.get("evidence_level_claimed", "E1")
    if order.get(claimed, 0) < order.get(required, 0):
        raise ValueError(f"EVIDENCE_LEVEL_TOO_LOW:claimed={claimed} required={required}")

"""Canonical Enforced Promotion Gate runner.

Contract:
- Always writes an Evidence Pack.
- Returns a structured result dict on success.
- Raises PromotionBlocked (or exits non-zero if invoked as CLI) on BLOCK.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

from .mode.resolver import resolve_mode
from .see.internal import see_internal
from .see.external import validate_external_items_minimum
from .mmd.detectors import mmd_detect
from .evidence.writer import EvidencePack
from .enforcement.consequence_handler import enforce_decision, PromotionBlocked


def _compute_external_see_requirement(target_channel: str, see_ctx: dict) -> tuple[bool, list[str]]:
    triggers: list[str] = []
    if target_channel in ("CANONICAL", "TRUSTED"):
        triggers.append("T1.1")
    if see_ctx.get("dependency_semantics_detected", False):
        triggers.append("T3.1")
    return (len(triggers) > 0), triggers


def run(
    candidate_path: str,
    target_channel: str,
    policy_bundle: Optional[str] = None,
    requested_mode: Optional[str] = None,
    evidence_root: str = "/mnt/data/metablooms_evidence",
    run_id: str = "PROMOTION-UNSPECIFIED",
    parent_evidence_id: Optional[str] = None,
    external_items: Optional[list[dict]] = None,
) -> Dict[str, Any]:
    mode = resolve_mode(requested_mode, target_channel)
    see_ctx = see_internal(candidate_path, policy_bundle)

    external_required, triggers = _compute_external_see_requirement(target_channel, see_ctx)
    external_items = external_items or []

    ep = EvidencePack.begin(
        evidence_root=evidence_root,
        run_id=run_id,
        parent_evidence_id=parent_evidence_id,
        mode_requested=requested_mode,
        mode_effective=mode,
        inputs={
            "candidate_path": candidate_path,
            "target_channel": target_channel,
            "policy_bundle": policy_bundle,
            "input_hashes": see_ctx.get("input_hashes", {}),
        },
        ecl_gates_active=[
            "CONSEQUENCE_BINDING_REQUIRED",
            "STRICT_MODE_REQUIRED",
            "EVIDENCE_REQUIRED",
            "EXTERNAL_SEE_REQUIRED_FOR_PROMOTION",
        ],
        see_block={
            "internal_complete": True,
            "external_required": external_required,
            "external_triggered_by": triggers,
            "external_items": [
                {
                    "item_id": it.get("item_id"),
                    "source_type": it.get("source_type"),
                    "source_locator": (it.get("source_locator", {}) or {}).get("canonical"),
                    "confidence": it.get("confidence"),
                    "content_hash": (it.get("content_hash", {}) or {}).get("value"),
                }
                for it in external_items
            ],
        },
    )

    mmd = mmd_detect(external_required, external_items)
    ep.set_mmd(mmd)

    # Minimal decision logic aligned to Gold Packs
    if external_required:
        ok, why = validate_external_items_minimum(external_items)
        if not ok:
            decision = {
                "decision_id": "DEC-001",
                "result": "FAIL",
                "reason_code": "EXT_SEE_REQUIRED_MISSING",
                "reasons": [why],
                "facts": {"external_see_items_count": len(external_items), "required_minimum": 2},
            }
        else:
            decision = {
                "decision_id": "DEC-002",
                "result": "PASS",
                "reason_code": None,
                "reasons": ["External SEE satisfied"],
                "facts": {"external_see_items_count": len(external_items)},
            }
    else:
        decision = {
            "decision_id": "DEC-002",
            "result": "PASS",
            "reason_code": None,
            "reasons": ["External SEE not required"],
            "facts": {"external_see_items_count": len(external_items)},
        }

    ep.set_decision(decision)

    try:
        consequence = enforce_decision(decision)
        ep.set_consequence(consequence)
        evidence_id = ep.finalize(final_status="PROMOTED")
        return {"ok": True, "evidence_id": evidence_id, "run_id": run_id}
    except PromotionBlocked as e:
        ep.set_consequence(e.consequence)
        evidence_id = ep.finalize(final_status="BLOCKED")
        raise

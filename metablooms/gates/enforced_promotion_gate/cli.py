import argparse
import json
import sys

from .mode.resolver import resolve_mode
from .see.internal import see_internal
from .see.external import load_external_items, validate_external_items_minimum
from .mmd.detectors import mmd_detect
from .evidence.writer import EvidencePack
from .enforcement.consequence_handler import enforce_decision, PromotionBlocked


def compute_external_see_requirement(target_channel: str, see_ctx: dict, policy_ctx: dict) -> tuple[bool, list[str]]:
    '''
    Minimal trigger mapping consistent with the staged delta pack:
      - T1.1: target_channel is CANONICAL or TRUSTED
      - T3.1: dependency/tool semantics involved
    '''
    triggers: list[str] = []
    if target_channel in ("CANONICAL", "TRUSTED"):
        triggers.append("T1.1")
    if policy_ctx.get("dependency_semantics", False) or see_ctx.get("dependency_semantics_detected", False):
        triggers.append("T3.1")
    required = len(triggers) > 0
    return required, triggers


def evaluate_promotion(external_required: bool, external_items: list[dict]) -> dict:
    '''Return a Decision object for ConsequenceHandler.'''
    if external_required:
        ok, why = validate_external_items_minimum(external_items)
        if not ok:
            return {
                "decision_id": "DEC-001",
                "result": "FAIL",
                "reason_code": "EXT_SEE_REQUIRED_MISSING",
                "reasons": [why],
                "facts": {
                    "external_see_items_count": len(external_items),
                    "required_minimum": 2
                }
            }
    return {
        "decision_id": "DEC-002",
        "result": "PASS",
        "reason_code": None,
        "reasons": ["External SEE satisfied" if external_required else "External SEE not required"],
        "facts": {"external_see_items_count": len(external_items)}
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="mb-promote")
    p.add_argument("--candidate", required=True, help="Path to candidate bundle (dir or file)")
    p.add_argument("--target", required=True, choices=["CANONICAL", "TRUSTED", "DEV"], help="Target channel")
    p.add_argument("--policy", default="", help="Path to policy bundle (dir or file)")
    p.add_argument("--requested-mode", default=None, choices=[None, "STRICT", "ADVISORY", "BYPASS"])
    p.add_argument("--evidence-dir", default="/mnt/data/metablooms_evidence", help="Evidence root directory")
    p.add_argument("--run-id", required=True, help="Run identifier")
    p.add_argument("--parent-evidence-id", default=None)
    p.add_argument("--external-evidence", action="append", default=[], help="Path to external SEE item JSON (repeatable)")
    args = p.parse_args(argv)

    mode = resolve_mode(args.requested_mode, args.target)
    see_ctx = see_internal(args.candidate, args.policy if args.policy else None)
    policy_ctx = {"dependency_semantics": see_ctx.get("dependency_semantics_detected", False)}

    external_required, triggers = compute_external_see_requirement(args.target, see_ctx, policy_ctx)
    external_items = load_external_items(args.external_evidence)

    ep = EvidencePack.begin(
        evidence_root=args.evidence_dir,
        run_id=args.run_id,
        parent_evidence_id=args.parent_evidence_id,
        mode_requested=args.requested_mode,
        mode_effective=mode,
        inputs={
            "candidate_path": args.candidate,
            "target_channel": args.target,
            "policy_bundle": args.policy or None,
            "input_hashes": see_ctx.get("input_hashes", {})
        },
        ecl_gates_active=[
            "CONSEQUENCE_BINDING_REQUIRED",
            "STRICT_MODE_REQUIRED",
            "EVIDENCE_REQUIRED",
            "EXTERNAL_SEE_REQUIRED_FOR_PROMOTION"
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
                    "content_hash": (it.get("content_hash", {}) or {}).get("value")
                } for it in external_items
            ]
        }
    )

    mmd = mmd_detect(external_required, external_items)
    ep.set_mmd(mmd)

    decision = evaluate_promotion(external_required, external_items)
    ep.set_decision(decision)

    try:
        consequence = enforce_decision(decision)
        ep.set_consequence(consequence)
        evidence_id = ep.finalize(final_status="PROMOTED")
        print(json.dumps({"ok": True, "evidence_id": evidence_id, "run_id": args.run_id}, indent=2))
        return 0
    except PromotionBlocked as e:
        ep.set_consequence(e.consequence)
        evidence_id = ep.finalize(final_status="BLOCKED")
        print(json.dumps({"ok": False, "evidence_id": evidence_id, "run_id": args.run_id, "reason_code": e.consequence.get("reason_code")}, indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

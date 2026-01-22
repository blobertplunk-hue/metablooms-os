"""Runtime router hook for MB_P0_DEBUG_GOVERNANCE_V1 (v1.1)

Responsibilities:
- Always write chat + project ledgers for CODE/DEBUG turns (append-only)
- Always emit heuristic_vs_metablooms telemetry events + update telemetry index
- Auto-invoke recursive controller to materialize loop artifacts for C2+ (no manual work)
- Invoke P0 gate (which performs fail-closed enforcement)

Required context:
- repo_root: filesystem root where artifacts/ledgers/telemetry are written
- mode: DEBUG|CODE
- claim_class: C0..C4
- artifacts: list[str] (project-relative)

Optional context:
- run_id, attempt_id, turn_id, project_id, external_facts_used, runtime_evidence_used
- iteration_outcomes: list[dict] for loop controller to append outcomes
"""

from __future__ import annotations

from typing import Any, Dict, List




def _extract_request_text(context: Dict[str, Any]) -> str:
    for k in ("user_prompt", "prompt", "request_text", "task_text", "message"):
        v = context.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _require_request_text(context: Dict[str, Any]) -> None:
    """Fail-closed if CODE/DEBUG/RESEARCH context lacks request text.

    This prevents bypass of auto-flagging and audit trails by omitting prompt fields.
    """
    mode = str(context.get("mode","")).upper()
    # Treat explicit research_required as RESEARCH intent too
    is_research = bool(context.get("research_required", False)) or mode == "RESEARCH"
    if mode in {"CODE", "DEBUG"} or is_research:
        text = _extract_request_text(context)
        if not text:
            raise RuntimeError(
                "P0 FAIL-CLOSED — request text missing. "
                "Context must include one of: user_prompt|prompt|request_text|task_text|message"
            )
        # Persist normalized request text key for downstream telemetry
        context["request_text_normalized"] = text

def _auto_flag_research(context: Dict[str, Any]) -> None:
    """Auto-flag research_required when the user requests up-to-date research/verification.

    This is a router-level choke point: it sets research_required=True based on intent signals
    in the request text. If no request text is available, it does nothing.
    """
    text = None
    for k in ("user_prompt", "prompt", "request_text", "task_text", "message"):
        v = context.get(k)
        if isinstance(v, str) and v.strip():
            text = v
            break
    if not text:
        return

    t = text.lower()
    triggers = [
        "up-to-date research",
        "up to date research",
        "do research",
        "research this",
        "web.run",
        "webrun",
        "sandcrawler",
        "look it up",
        "verify",
        "validate",
        "citations",
        "sources",
        "external research",
        "browse the web",
    ]
    if any(x in t for x in triggers):
        context["research_required"] = True
        # Mark that router inferred the requirement (for telemetry/ledger later)
        context["research_auto_flagged"] = True

def enforce_p0_dcc(context: Dict[str, Any]) -> Dict[str, Any]:
    # Validate minimally
    if not isinstance(context, dict):
        raise RuntimeError("context must be dict")
    repo_root = context.get("repo_root")
    if not repo_root:
        raise RuntimeError("repo_root required")
    artifacts = context.get("artifacts") or []

    # Auto-flag research intent based on request text
    _auto_flag_research(context)
    if not isinstance(artifacts, list):
        raise RuntimeError("artifacts must be list[str]")

    # Append-only ledgers (chat + project)
    from metablooms_runtime.ledgering.writers import write_chat_ledger, write_project_ledger  # type: ignore
    turn_id = context.get("turn_id", "TURN_UNKNOWN")
    project_id = context.get("project_id", "PROJECT_UNKNOWN")

    write_chat_ledger(str(repo_root), {
        "turn_id": turn_id,
        "mode": context.get("mode"),
        "claim_class": context.get("claim_class"),
        "external_facts_used": bool(context.get("external_facts_used", False)),
        "runtime_evidence_used": bool(context.get("runtime_evidence_used", False)),
    })

    write_project_ledger(str(repo_root), {
        "project_id": project_id,
        "turn_id": turn_id,
        "mode": context.get("mode"),
        "claim_class": context.get("claim_class"),
        "event": "P0_DCC_ENFORCE_CALLED"
    })

    # Telemetry: heuristic vs metablooms event + index update
    from metablooms_runtime.telemetry.writers import write_hvm_event, upsert_index  # type: ignore
    write_hvm_event(str(repo_root), {
        "turn_id": turn_id,
        "project_id": project_id,
        "phase": "enforce_entry",
        "note": "P0DCC enforcement invoked"
    })
    upsert_index(str(repo_root))

    # Auto-run loop controller for C2+ to materialize loop artifacts and optionally append iteration outcomes
    claim_class = str(context.get("claim_class", "")).upper()
    if claim_class in {"C2", "C3", "C4"}:
        from metablooms.governance.p0_dcc_v1.see_recursive_controller_v1 import run_loop  # type: ignore
        iteration_outcomes = context.get("iteration_outcomes", None)
        run_loop(repo_root=str(repo_root), context=context, max_iters=int(context.get("max_iters", 3)), iteration_outcomes=iteration_outcomes)

        # Ensure artifacts list includes loop outputs (no manual step)
        aset = set(artifacts)
        aset.add("loop/LOOP_RECEIPTS.json")
        aset.add("loop/LOOP_SUMMARY.md")
        # If certified, controller writes ecl/ECL_PASS.json; include if it exists
        from pathlib import Path
        if (Path(str(repo_root)) / "ecl" / "ECL_PASS.json").exists():
            aset.add("ecl/ECL_PASS.json")
        context["artifacts"] = sorted(aset)

    # Invoke the P0 gate
    from metablooms.governance.p0_dcc_v1 import mb_p0_debug_gate as gate  # type: ignore
    gate.enforce(context)

    # Post-telemetry
    write_hvm_event(str(repo_root), {
        "turn_id": turn_id,
        "project_id": project_id,
        "phase": "enforce_exit",
        "note": "P0DCC enforcement completed"
    })
    upsert_index(str(repo_root))

    return context

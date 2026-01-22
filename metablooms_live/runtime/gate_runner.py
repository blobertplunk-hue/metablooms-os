"""Runtime gate runner (P0)

Preflight:
- Materialize research structures (claims/citation skeleton; inject created_ts if missing)
- Enforce Rule-of-Three + Delta-on-retry prerequisites
- Enforce P0DCC router (loop/ECL/ledgers/telemetry) via mandatory runtime entrypoint

Postflight:
- Enforce research evidence + citation coverage + claim↔receipt↔timestamp binding (when research is required)
- Enforce staging → commit
"""

from typing import Dict, Any

def run_preflight(context: Dict[str, Any]) -> None:
    from metablooms_runtime.invariants.research_materializer import enforce as materialize_research
    from metablooms_runtime.invariants.rule_of_three_invariant import enforce as rule3_enforce
    from metablooms_runtime.invariants.delta_required_invariant import enforce as delta_enforce

    materialize_research(context)
    rule3_enforce(context)
    delta_enforce(context)

    from runtime.routers.p0_dcc_router import enforce_p0_dcc
    enforce_p0_dcc(context)

def run_postflight(context: Dict[str, Any]) -> None:
    from metablooms_runtime.invariants.research_invariant import enforce as research_enforce
    from metablooms_runtime.invariants.citation_density_invariant import enforce as citation_enforce
    from metablooms_runtime.invariants.claim_receipt_timestamp_invariant import enforce as crt_enforce
    from metablooms_live.runtime.staging_commit import enforce as commit_enforce

    research_enforce(context)
    citation_enforce(context)
    crt_enforce(context)
    commit_enforce(context)

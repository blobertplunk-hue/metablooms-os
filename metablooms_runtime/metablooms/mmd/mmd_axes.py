# ECL_VERSION: 1.0
# ECL_SCOPE: metablooms.mmd.mmd_axes
# ECL_RESPONSIBILITY: Detect missing-middle gaps deterministically; emit typed MMDFinding objects.

from __future__ import annotations

from typing import List

from metablooms.schemas.mmd_finding import MMDFinding, MMDAxis, MMDSeverity


class MMDResult:
    def __init__(self, findings: List[MMDFinding]):
        self.findings = findings

    @property
    def has_blockers(self) -> bool:
        return any(f.severity == MMDSeverity.BLOCK for f in self.findings)


def _mk_finding(
    *,
    axis: MMDAxis,
    severity: MMDSeverity,
    missing_link: str,
    finding_id_suffix: str,
    responsible_segment: str | None = None,
    remediation_hint: str | None = None,
    details: dict | None = None,
) -> MMDFinding:
    """Create an MMDFinding aligned to the schema."""
    fid = f"{axis.value}:{finding_id_suffix}"
    return MMDFinding(
        finding_id=fid,
        axis=axis,
        severity=severity,
        missing_link=missing_link,
        responsible_segment=responsible_segment,
        remediation_hint=remediation_hint,
        details=details or {},
    )


def detect_plan_code(plan: dict, code_refs: List[str]) -> List[MMDFinding]:
    findings: List[MMDFinding] = []
    if plan and not code_refs:
        findings.append(
            _mk_finding(
                axis=MMDAxis.PLAN_CODE,
                severity=MMDSeverity.BLOCK,
                missing_link="Plan exists but no code artifacts referenced.",
                finding_id_suffix="plan_without_code",
                responsible_segment="executor",
                remediation_hint="Attach concrete code_refs (paths/ids) to the plan execution output.",
                details={"plan_present": True, "code_ref_count": 0},
            )
        )
    return findings


def detect_code_evidence(code_refs: List[str], evidence_pointers: list) -> List[MMDFinding]:
    findings: List[MMDFinding] = []
    if code_refs and not evidence_pointers:
        findings.append(
            _mk_finding(
                axis=MMDAxis.CODE_EVIDENCE,
                severity=MMDSeverity.BLOCK,
                missing_link="Code artifacts exist but no evidence pointers produced.",
                finding_id_suffix="code_without_evidence",
                responsible_segment="see",
                remediation_hint="Emit evidence_pointers aligned to EvidencePointer schema for each claim.",
                details={"code_ref_count": len(code_refs), "evidence_pointer_count": 0},
            )
        )
    return findings


def detect_evidence_gate(evidence_pointers: list, gate_passed: bool) -> List[MMDFinding]:
    findings: List[MMDFinding] = []
    if evidence_pointers and not gate_passed:
        findings.append(
            _mk_finding(
                axis=MMDAxis.EVIDENCE_GATE,
                severity=MMDSeverity.BLOCK,
                missing_link="Evidence exists but governance gate not passed.",
                finding_id_suffix="evidence_without_gate",
                responsible_segment="gate",
                remediation_hint="Ensure governance gate validates evidence pack + claimset before proceeding.",
                details={"evidence_pointer_count": len(evidence_pointers), "gate_passed": False},
            )
        )
    return findings


def detect_loop_convergence(iteration: int, max_iterations: int, improved: bool) -> List[MMDFinding]:
    findings: List[MMDFinding] = []
    if iteration >= max_iterations and not improved:
        findings.append(
            _mk_finding(
                axis=MMDAxis.LOOP_CONVERGENCE,
                severity=MMDSeverity.BLOCK,
                missing_link="Loop exhausted without measurable improvement.",
                finding_id_suffix="no_convergence",
                responsible_segment="see",
                remediation_hint="Switch strategy or fail-closed with explicit stop reason and evidence receipts.",
                details={"iteration": iteration, "max_iterations": max_iterations, "improved": False},
            )
        )
    return findings


def run_mmd(
    *,
    plan: dict,
    code_refs: List[str],
    evidence_pointers: list,
    gate_passed: bool,
    iteration: int,
    max_iterations: int,
    improved: bool,
) -> MMDResult:
    findings: List[MMDFinding] = []
    findings += detect_plan_code(plan, code_refs)
    findings += detect_code_evidence(code_refs, evidence_pointers)
    findings += detect_evidence_gate(evidence_pointers, gate_passed)
    findings += detect_loop_convergence(iteration, max_iterations, improved)
    return MMDResult(findings)

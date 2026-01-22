# METABLOOMS_P0_INVARIANT_FRAMEWORK.md
MetaBlooms — P0 Invariant Framework (Governance-Heavy Coding Standard)

This document captures the governance-first coding standard that prioritizes auditability
and deterministic safety over raw execution speed.

## 1) The Core Governance Principles (P0) — Seven Non‑Negotiables

**P0-1: Prove‑before‑claim**  
All correctness or completion claims must be backed by replayable evidence (tool telemetry, artifact inspection, hashes, or captured stdout/stderr).

**P0-2: Fatigue‑proof automation**  
Mandatory automated checks for things humans skip: syntax parsing, deterministic naming, schema validation, and preflight gating.

**P0-3: Hostile to silent failure**  
Success is never reported unless it can be proven. Failures must emit specific reason codes (e.g., `GATE_FAILED`, `WRITE_BLOCKED`, `EVIDENCE_MISSING`).

**P0-4: Structure carries intent**  
Work is separated into four phases: **Probe (Observe)** → **Decide (Plan)** → **Act (Side effects)** → **Verify (Confirm)**. No phase skipping.

**P0-5: Long‑horizon compatibility**  
Outputs are date‑prefixed and versioned; formats are future‑readable; backward‑compatibility stance is explicit.

**P0-6: Adaptable without fragility**  
Extensibility is driven by registries/configuration files rather than scattered conditional logic.

**P0-7: Debuggability is first‑class**  
Every failure emits: reason codes, context, evidence pointers, and a recovery plan.

## 2) Operational Execution Loop (Typical Enforcement Pattern)

A compliant run generally enforces:
- **Environment validation:** verify writable base paths; if not, `WRITE_BLOCKED: BASE_PATH_MISSING_OR_UNWRITABLE`.
- **Overwrite prevention:** deterministic output paths may not be overwritten; if present, `WRITE_BLOCKED: WOULD_OVERWRITE`.
- **Atomic writing:** write to a temp file, then replace/move to final destination.
- **Verification & hashing:** confirm post-write existence; compute SHA‑256 hashes.
- **Evidence recording:** emit machine-readable evidence JSON and append-only human ledger entries.

## 3) Artifacts of Truth (Audit Trail)

Typical artifacts:
- **P0 Invariant File:** Binding requirements for a subsystem (this file).
- **Evidence Record:** Machine-readable proof of a specific sweep/run.
- **Evidence Log / Ledger:** Append-only human-readable record of actions and proofs.

## 4) Relationship to MetaBlooms OS v2.0 Spec

This P0 framework is compatible with (and intended to be enforced by):
- `METABLOOMS_KERNEL_v2.md`
- `METABLOOMS_PIPELINES.md`
- `METABLOOMS_HEURISTIC_REGISTRY.md`
- `METABLOOMS_V2_COMPLIANCE_CHECKLIST.md`

End of METABLOOMS_P0_INVARIANT_FRAMEWORK.md

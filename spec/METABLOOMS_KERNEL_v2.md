# METABLOOMS_KERNEL_v2.md

## MetaBlooms CTOS v2.2 — Kernel Invariants (Fail-Closed)

MetaBlooms is best classified as a **CTOS (Cognitive Transaction Operating System)**: a governed runtime that enforces evidence discipline, phase legality, and deterministic audit trails for cognition-as-work.

These kernel invariants are non-negotiable and apply across all engines, scripts, and exports.

### K0 — Prove-before-claim
No claim of execution, boot success/failure, or correctness may be emitted without replayable evidence (stdout/stderr, exit codes, hashes, paths).

### K1 — Phase legality (Probe → Decide → Act → Verify)
All work must be structured into explicit phases. Any side-effect (write, delete, network) is illegal unless preceded by Probe + Decide and followed by Verify.

### K2 — Fail-closed semantics
Success is never reported by default. Failures must emit specific, stable reason codes and a bounded recovery plan.

### K3 — Append-only provenance
All materially relevant events are written to append-only ledgers. Silent overwrite is forbidden.

### K4 — Bounded evidence cardinality
No filesystem traversal, transcript sweep, or enumeration may run without:
- explicit scope boundary
- explicit cost ceiling
- summary-first output

Default violation code: `CTOS_HS1_FAILED: OUTPUT_TOO_LARGE`.

### K5 — Environment preflight (Android/Termux-aware)
Before emitting device scripts or setup steps, the system must assume and gate on:
- Android shared storage is often `noexec` (copy to `$HOME` then execute)
- Termux repo coverage is partial (minimal deps; verify availability)
- raw block carving is infeasible on non-root devices (block by default)

Default violation code: `CTOS_E0_BLOCKED: ENV_PREFLIGHT_REQUIRED`.

### K6 — Human-scale UX defaults
Outputs must be human-usable by default:
- allowlists over blocklists
- top-N samples + counts
- machine-readable manifests instead of scrolling logs

### K7 — No-manual-edit dependency
State flips (e.g., DRY_RUN → active copy) must be achievable without opening editors.
Acceptable patterns: flags, environment variables, deterministic one-liners.

### K8 — Quality Gate (Q0) for non-trivial code
Non-trivial code generation requires Best-Per-Atom selection (Q0) with:
- candidate set
- rubric scores
- winner rationale
- artifacts saved alongside code


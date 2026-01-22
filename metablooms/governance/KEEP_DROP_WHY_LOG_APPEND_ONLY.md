# KEEP / DROP / WHY — Append-Only Log

## 2026-01-16T00:00-0600 — INIT
- objective_key: AUTOSAVE_GOVERNANCE
- change_type: ADD
- keep:
  - autosave exports on every wiring commit
  - append-only changelog
  - explicit commit boundary "WIRE THIS IN NOW"
- drop:
  - implicit/unlogged wiring decisions
  - silent drift
- why_keep: "Durable state and auditability prevent regressions and rework loops."
- why_drop: "Unlogged decisions recreate Archive2 dynamics."
- supersedes: "N/A"

# MetaBlooms Artifact Dating + “Latest/Best” Resolution (Spec v1)

**Created (UTC):** 2026-01-08T20:14:54Z

## Problem
MetaBlooms produces multiple artifacts over time (OS ZIPs, proof reports, deltas, indexes). Without a **canonical dating/marking system**:
- humans and agents “guess” which artifact is authoritative
- stale bundles get treated as latest
- “proof” artifacts can be mistaken for shippable OS bundles
- regressions occur when selection logic drifts

## Goal
Introduce a deterministic mechanism that:
1) **Metadates** each shipped artifact consistently
2) Provides a canonical **Latest/Best pointer**
3) Includes a **fallback selection check** if metadata is incomplete
4) Is mechanically verifiable (validator-gated)

---

## Core Concepts

### A) Artifact Metadata (required)
Every shippable artifact MUST have a sidecar JSON file:

**Rule:** `X.ext` must have `X.ext.meta.json`

Minimum fields:
- `artifact_id` (stable string; e.g., `metablooms_os_cumulative`)
- `artifact_type` (enum: `os_zip`, `boot_proof`, `delta`, `spec`, `report`)
- `version` (semver string: `MAJOR.MINOR.PATCH`)
- `created_utc` (RFC3339 UTC)
- `sha256` (hex for binary artifacts; optional for text)
- `source` (where it came from; e.g., “built by MetaBlooms pipeline”)
- `governance_status` (enum: `unknown`, `boot_verified`, `baseline_frozen`, `deprecated`)
- `evidence` (object; references proof artifacts by filename)
- `notes` (string, optional)

### B) Canonical Latest/Best Pointer (required)
A single file in the OS root controls selection:

**`LATEST.json`**
- `latest_os_zip` (filename)
- `best_os_zip` (filename; may equal latest)
- `baseline_v1_os_zip` (filename)
- `updated_utc`
- `selector_version` (e.g., `1.0`)
- `selection_evidence` (array of filenames used to justify pointer)

**Interpretation**
- **latest** = highest semver that is boot-verified
- **best** = highest semver that is boot-verified AND passes all required validators AND not deprecated
- **baseline_v1** = frozen reference point (never overwritten)

### C) Fallback “Best” Check (when metadata is missing)
If meta files are absent or incomplete, selection falls back to evidence search:
- enumerate candidate `MetaBlooms_OS_CUMULATIVE_*.zip`
- for each candidate, require:
  - `.sha256` exists and matches
  - a boot proof artifact exists that names the ZIP (or a ledger event references produced_zip)
  - required validators listed as OK (proof or ledger)
- pick highest semver among those that meet evidence requirements

This makes “best” discoverable even if someone forgot to mark metadata.

---

## Mechanical Gates (validators)
Add validators (boot or export stage):
1) **ARTIFACT_METADATA_REQUIRED_V1**
   - every shipped OS ZIP must have `.sha256` + `.meta.json`
2) **LATEST_POINTER_VALID_V1**
   - `LATEST.json` must exist
   - pointed ZIPs must exist and have matching metadata
   - `best` must not be older than `latest` unless justified via `governance_status` or validator failure evidence
3) **FALLBACK_SELECTION_CONSISTENT_V1**
   - if metadata missing, fallback selection must still identify the same `best` as `LATEST.json` OR fail closed

---

## Where this belongs
This system must be enforced at **export/shipping time** (EXPORT_POLICY gate) and validated at **boot** (so stale pointers cannot survive).

---

## Deliverables (minimum viable implementation)
- `LATEST.json` (canonical pointer)
- `artifact_registry.ndjson` or `ARTIFACT_REGISTRY.json` (optional; for inventory)
- `artifact_resolver_latest_best.py` (deterministic resolver + proof generator)
- Validators described above (in separate deltas if you prefer modularity)


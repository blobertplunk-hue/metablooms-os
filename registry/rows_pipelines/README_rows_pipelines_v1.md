# ROW + Pipeline Indexing (Official)

Authority: MetaBlooms OS Runtime
Status: OFFICIAL
Version: v1

## Objective
Provide a deterministic, reusable, evidence-backed way to:
- index ROWs (Routed Operational Workflows) and Pipelines from chat artifacts (e.g., Artifact 2),
- keep raw mentions auditable without contaminating canonical runtime registries,
- promote/improve suboptimal definitions via a gated promotion queue,
- resolve aliases and merges without breaking references.

## 3-Layer model (do not collapse)
1) Evidence Index (immutable, append-only)
2) Sectioned Candidate Registries (recall-oriented)
3) Canonical Registries (runtime-oriented; operational specs only)

## Paths (canonical)
- Contracts (schemas/routing): `/contracts/*` (authoritative)
- Artifact2 source index: `/registry/artifact2_rows_pipelines/*` (sectioned candidates + evidence)
- Official manifest: `/registry/rows_pipelines/index_manifest.json`
- Canonical registries:
  - `/registry/rows_pipelines/canonical/rows_canonical.json`
  - `/registry/rows_pipelines/canonical/pipelines_canonical.json`
  - `/registry/rows_pipelines/canonical/aliases.json`
  - `/registry/rows_pipelines/canonical/supersedes.json`

## Promotion rule (fail-closed)
- Candidate items may be promoted into canonical only if they include:
  - triggers
  - inputs/outputs
  - steps
  - gates
  - artifacts (paths or naming convention)
- Mentions-only remain in candidate registries and are added to `improvement_queue`.

## Runtime access
Use: `runtime.lib.rows_pipelines_registry`.

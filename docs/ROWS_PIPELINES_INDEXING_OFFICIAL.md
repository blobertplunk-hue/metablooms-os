# Official ROW + Pipeline Indexing

This OS ships an official, evidence-first method for indexing and mapping ROWs and Pipelines.

## What is official
- Contracts and routing live at `/contracts/*`.
- Artifact-derived indexes live under `/registry/artifact2_rows_pipelines/*` (sectioned).
- The official manifest is `/registry/rows_pipelines/index_manifest.json`.
- Runtime loading is provided by `runtime.lib.rows_pipelines_registry`.

## How to extend (append-only)
1) Add a new Artifact2 section registry: `/registry/artifact2_rows_pipelines/sections/section_XXX_to_YYY.*`
2) Update `/registry/artifact2_rows_pipelines/index_manifest.json` (append new section entry)
3) Improve/promote by updating canonical files under `/registry/rows_pipelines/canonical/*`.

## Fail-closed rules
- Runtime consumers must load the official manifest; if missing, treat as NOT_AVAILABLE.
- Canonical registries must never contain mention-only items.

# Provenance Schema (Reduced) — v1

## Goal
Provide durable traceability without importing the early “Provenance Engine” bloat.

## Required Fields (ONLY these are mandatory)
1. `origin` — where the item came from (source artifact, conversation, file, or user directive)
2. `mutation_reason` — why it changed (trigger, bugfix, governance requirement)
3. `supersedes` — what it replaces (path/id/version); use `N/A` if none

## Where Required
- All P0 and P1 changes
- Optional for P2+

## Fail-Closed Rule
If a P0/P1 change lacks provenance fields, the change must not be committed/exported.

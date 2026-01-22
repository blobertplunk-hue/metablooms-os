# FAIL_TO_FIX_POLICY.md (P0)

## Goal
Hardening failures should be repaired automatically when safe. The system remains fail-closed if repair cannot restore compliance.

## Class A: Quarantine (automatic)
Used for historical notes and non-authoritative documents. Action: move to `docs/_historical/` and annotate.

## Class B: Controlled rewrite (automatic, constrained)
Used when a forbidden term appears in a non-canonical document and a deterministic replacement exists. Action: rewrite the term, add an AUTO_REWRITE marker, log the change, rescan.

## Never auto-repair
Canonical ontology and literal architecture docs are never auto-edited. Violations there are P0 and require explicit governance.

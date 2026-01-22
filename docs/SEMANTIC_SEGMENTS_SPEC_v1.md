# MetaBlooms Semantic Segments (Pipeline) — Spec v1

## Purpose
Define a **machine-readable semantic segmentation layer** for MetaBlooms pipelines so that:
- every pipeline stage is **typed** (semantic segment),
- LLM work is **scoped** to segment contracts (not ad hoc),
- validators/gates can reason over **meaningful units** (not raw files),
- ledgers can record **segment-level evidence** and repairs.

This is an *OS mechanism*, not a writing convention.

---

## Core Concepts

### Semantic Segment
A named, versioned contract that defines:
- intent
- required inputs
- produced artifacts
- allowed operations
- forbidden behaviors
- validation and evidence requirements
- escalation rules

### Segment Instance
A run-time occurrence of a segment, identified by `segment_instance_id`, with evidence pointers.

### Segment Registry
A canonical registry of all segments, their IDs, and enforcement rules.

---

## Canonical IDs
- `SEG.<DOMAIN>.<NAME>.V<MAJOR>` (e.g., `SEG.PIPELINE.INGEST.V1`)
- Gates/validators MUST reference segment IDs exactly.

---

## Required Files (Canonical Paths)
- `metablooms/registry/semantic_segments_v1.json`
- `metablooms/validators/mb_validate_semantic_segments_v1.py` (enforces schema + invariants)
- `metablooms/preflight/gates/mb_gate_semantic_segments_required_v1.py` (boot/publish enforcement hook)

---

## Minimal Invariants (P0)
1. Every pipeline stage MUST declare `segment_id`.
2. Every declared `segment_id` MUST exist in the registry.
3. Each segment MUST define:
   - `intent`
   - `required_inputs`
   - `produces`
   - `allowed_ops`
   - `forbidden_ops`
   - `validators`
   - `evidence_requirements`
4. Segments that allow LLM interaction MUST define:
   - `llm_role` (one of: `CLASSIFY`, `MAP`, `PROPOSE`, `EXPLAIN`, `REWRITE_CONTROLLED`)
   - `constraints_ref` (pointer to ontology/contract)

---

## Practical Outcome
This creates the systemic behavior you described:
- the pipeline becomes a sequence of **semantic segments**
- LLM behavior becomes role-bound within segments
- “semantic debugging/fixing” becomes a governed repair segment rather than an ad hoc patch

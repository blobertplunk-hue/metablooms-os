# MetaBlooms SDI-02 — Compliance Validator (SDI-02-VAL)
## Version 1.0 (for SDI-02 v1.0.1) — Append-only

This validator is a **hard gate**: SDI-02 execution is considered **FAILED** unless the run produces a valid **Run Manifest** and passes every check below.

---
## Why this exists
Prompt-only compliance is not sufficient. SDI-02-VAL forces:
- evidence-backed extraction (no hallucination)
- non-compressed outputs (all required artifacts)
- deterministic structure (sheets/blocks/rules)
- professional communication deliverables

---
## Required outputs (must exist)
A run is valid only if ALL are produced:

1) **Excel workbook** with required sheets:
- Signal (Reading)
- Narrative / Instructional
- Evidence Trace

2) **Professional communication outputs**:
- Class-level literacy narrative
- Student-level talking points (2–4 bullets per student)
- Explicit exclusions (what is not being taught and why)

3) **Run Manifest JSON** (machine-checkable) conforming to the schema in this pack.

---
## Gate rules (MUST PASS)
### G0 — Intake gate
- Confirms BOY+MOY window consistency OR explicitly flags mismatch and halts.
- Confirms domains present OR flags missing and halts.

### G1 — Source authority gate
- Manifest must declare which files were used for:
  - scores/placements (Diagnostic PDFs)
  - typical growth (Growth PDF)
  - skill descriptors (CSVs)
- If any field is populated from a lower authority source, manifest must include a conflict note.

### G2 — Forensic extraction gate
- Manifest must include `no_inference_attestation = true`
- Manifest must include `blank_cell_policy = "prefer_blank_over_guess"`

### G3 — Spreadsheet architecture gate
Workbook must meet invariants:
- Names never wrap/clip (design intent; validator requires a manual check checkbox = true)
- Signal sheet: no prose blocks; values only
- Narrative sheet: no raw scores/placement bands
- Evidence Trace: each student is exactly a 3-row block

### G4 — Color logic gate
Manifest must include the growth thresholds:
- green_if_delta_ge_typical_plus = 3
- yellow_if_abs_delta_minus_typical_le = 2
- red_if_delta_lt_typical_minus = 2
and must confirm they were applied.

### G5 — Completeness gate
Manifest `roster.student_count` must match the workbook roster count.
If mismatch, run fails unless `explicit_exclusion_list` is present and justified.

### G6 — Communication gate
Manifest must confirm:
- class narrative produced
- per-student bullets produced
- exclusions produced

---
## How SDI-02 must use this validator (wired behavior)
SDI-02 execution must follow this sequence:

1) Execute SDI-02 stages 0–7
2) Generate workbook + comm outputs
3) Generate Run Manifest JSON
4) Run SDI-02-VAL checks (self-check)
5) If any check fails: **revise outputs** and repeat steps 2–4

A run may not be presented to the user as “complete” unless SDI-02-VAL passes.

---
## Minimal “Validator Prompt” (for tool-less environments)
Use exactly this as a final step in any chat run:

"""
Run SDI-02-VAL. Produce a Run Manifest JSON that conforms to the schema. Then list PASS/FAIL for G0–G6 with one-sentence justification each. If any FAIL, revise the outputs and re-run until all PASS.
"""

---
## Versioning
- SDI-02-VAL v1.0 validates SDI-02 v1.0.1
- Any change to SDI-02 rules → update SDI-02-VAL and bump version.

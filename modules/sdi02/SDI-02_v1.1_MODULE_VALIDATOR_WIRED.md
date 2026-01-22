
# MetaBlooms Module: SDI-02 — Student Diagnostic Intelligence
## Version 1.1 (FROZEN) — Lossless / Non-Compressed
## VALIDATOR-WIRED (Requires SDI-02-VAL v1.0)

================================================================
THIS MODULE IS NOT COMPLETE UNLESS SDI-02-VAL PASSES (G0–G6).
PROMPT-ONLY COMPLIANCE IS NOT ACCEPTED.
================================================================

## REQUIRED DEPENDENCY
- **SDI-02-VAL v1.0** (MetaBlooms Compliance Validator for SDI-02)
  - You must provide a **Run Manifest JSON** and PASS all gates G0–G6.
  - If any gate FAILS, SDI-02 MUST revise outputs and re-run validation until PASS.

---
## EXACT INVOCATION COMMANDS (SELF-CONTAINED)

In ANY new chat, do the following IN ORDER.

### Step 1 — Upload files
Upload:
1) `MetaBlooms_SDI-02_v1.1_MODULE_VALIDATOR_WIRED.md` (this file)
2) `SDI-02-VAL_v1.0.md`
3) `SDI-02_Run_Manifest.schema.json`
4) i-Ready PDFs + (optional) CSVs

### Step 2 — Say EXACTLY:
"Load MetaBlooms modules SDI-02 v1.1 and SDI-02-VAL v1.0. These modules are authoritative and must be obeyed exactly. Do not summarize, compress, or reinterpret them. Execute SDI-02 through all stages, then run SDI-02-VAL and do not stop until all gates G0–G6 are PASS. Output the workbook and the Run Manifest JSON."

If the system asks clarifying questions instead of executing, repeat Step 2 verbatim.

---
## PURPOSE
SDI-02 converts i-Ready Reading diagnostics into STAAR-optimized instructional decisions,
artifacts, and professional explanations. It is designed to be repeatable across chats
without rework, inference drift, or compression.

It supports:
- Accurate forensic extraction
- High-ROI instructional grouping
- STAAR-aligned decision logic
- Literacy check-ins and defensible professional explanation

---
## REQUIRED INPUTS
- i-Ready Reading Diagnostic PDFs (BOY + MOY, same window)
- i-Ready Growth Report PDF
- i-Ready Personalized Instruction CSVs (optional)

If any required input is missing:
- HALT
- Flag missing items
- Do NOT proceed to analysis

---
## EXECUTION PIPELINE (MANDATORY ORDER)

### STAGE 0 — INTAKE VALIDATION
Verify:
- Same diagnostic window
- Domains present
- Vertical scale consistency
- Goal = STAAR Reading growth

No analysis before pass.

---
### STAGE 1 — FORENSIC DATA EXTRACTION (NO INFERENCE)
Rules:
- Extract only explicitly stated values.
- No inference, no cause attribution, no “likely” claims.
- Blank cells are correct if data is absent.

Source Authority:
1. Diagnostic PDFs (scores, placements)
2. Growth Report PDF (typical growth, percent progress)
3. CSVs (skill descriptors only)

Discard automatically:
- Motivational language
- Boilerplate
- Generic recommendations
- Marketing phrases

Conflict handling:
- Higher authority wins
- Conflict noted in Evidence Trace

---
### STAGE 2 — CONSTRAINT DETECTION (A-07)
Determine class-level:
- Primary STAAR bottleneck
- Secondary constraint
- Non-constraints

Priority order:
1. Comprehension
2. Vocabulary → Meaning
3. Fluency
4. Phonics
5. Test Processing

---
### STAGE 3 — STUDENT LEVERAGE CLASSIFICATION
Each student assigned ONE lane only.

Lane priority:
1. Comprehension Core
2. Vocabulary → Comprehension Bridge
3. Fluency Support
4. Phonics Repair
5. Test Readiness

Placement bands override raw score changes:
- Same band BOY→MOY = YELLOW (flat)
- Higher band = GREEN
- Lower band = LIGHT RED

---
### STAGE 4 — GROUP FORMATION
Reduce to instructional lanes with:
- Shared leverage
- STAAR alignment
- Exit criteria

No double-assignment.

---
### STAGE 5 — ARTIFACT CONSTRUCTION (EXCEL)

#### SHEET 1 — SIGNAL (READING)
- BOY / MOY in paired columns
- No wrapping
- One value per cell
- No prose

Growth color logic:
Δ = MOY − BOY, T = Typical Growth
- Δ ≥ T + 3 → GREEN
- |Δ − T| ≤ 2 → YELLOW
- Δ < T − 2 OR Δ < 0 → LIGHT RED

#### SHEET 2 — NARRATIVE / INSTRUCTIONAL
- Wrapped text
- Bulleted (3–5 max per student)
- NO raw scores or placement labels

#### SHEET 3 — EVIDENCE TRACE
Each student = EXACTLY 3 rows:
1. Scale + Placement
2. Growth vs Typical
3. Domain Placements (Phonics, HFW, Vocab, Comp)

Formatting:
- Thick outer border per student block
- Thin internal grid
- White space between student blocks

---
## VISUAL COGNITION INVARIANTS
- Names never clip or wrap
- Signal columns narrow; narrative columns wide
- Wrapping only in narrative
- One concept per cell
- Color = one meaning per layer
- Student blocks visually distinct (thick outer border; thin interior)

---
## STAGE 6 — SELF-AUDIT (MANDATORY)
Before claiming completion:
- No inferred data
- No over-compression
- No prose in signal sheet
- Narrative contains no raw scores
- Visual scan <2 seconds per student
- Instruction follows constraint priority

If any fail → revise outputs BEFORE validator run.

---
## STAGE 7 — PROFESSIONAL COMMUNICATION OUTPUTS (REQUIRED)
Produce:
1) Class-level literacy narrative (meeting-ready, evidence-grounded)
2) Student-level talking points (2–4 bullets per student)
3) Explicit exclusions (what is NOT being taught now and why)

---
## STAGE 8 — VALIDATOR GATE (SDI-02-VAL)
After producing outputs:
1) Generate **Run Manifest JSON** conforming to `SDI-02_Run_Manifest.schema.json`
2) Run SDI-02-VAL and report PASS/FAIL for G0–G6 with 1-sentence justification each
3) If any FAIL: revise outputs and re-run until all PASS

A run is NOT COMPLETE unless SDI-02-VAL returns all PASS.

---
## CHANGE POLICY
- Append-only
- Any rule change → version bump (v1.2, v2.0, etc.)
- This version is safe to reuse when paired with SDI-02-VAL v1.0

END OF MODULE

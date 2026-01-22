# META BLOOMS — P0 DEBUG + CODE CONSTITUTION (CANONICAL)

**Version:** P0-DCC-v1  
**Status:** LOCKED (SPEC)  
**Applies To:** All coding and debugging activities at claim class **C2 or higher** (and any lower class invoking external facts).

---

## I. PURPOSE (NON-NEGOTIABLE)
This constitution ensures:
1) No code or fix is accepted on confidence alone
2) No debugging terminates without evidence-backed convergence
3) External reality is consulted when claims depend on it
4) Reasoning gaps are mechanically blocked
5) Evidence strength scales with claim impact
6) Reliability becomes a system property, not an operator skill

---

## II. CORE SYSTEMS (AUTHORITATIVE DEFINITIONS)

### SEE — Sandcrawler Evidence Engine
- Performs **mandatory external research** using **WebRun** when claims depend on real-world facts
- Requires:
  - WebRun queries
  - Source excerpts
  - Citations
  - Structured evidence normalization
  - Evidence summaries
- **Fail-closed** if not run when required

### MMD — Missing Middle Detector
- Detects skipped reasoning, missing causal steps, missing transformations, or missing validation
- Blocks progress if any A→B jump is not explicitly shown and evidenced

### ECL — Extraordinary Code Law
- Classifies claims by impact (C0–C4)
- Scales required proof accordingly
- Rejects claims whose evidence does not meet the required threshold

### Telemetry / Observability
- Converts runtime behavior into correlated, machine-inspectable evidence
- Requires correlation keys (`run_id`, `attempt_id`, `hypothesis_id`, etc.)
- Uncorrelated runtime claims are invalid

### Recursive Loop (User-originated, Canonical)
- A bounded loop:
  1. Propose hypothesis
  2. Generate minimal change
  3. Execute / test
  4. Capture evidence
  5. MMD check
  6. ECL check
  7. Certify or refine and repeat
- **One-shot attempts are not allowed** for non-trivial work

---

## III. CLAIM CLASSIFICATION (ECL)

```text
C0 – Cosmetic / trivial
C1 – Local functional
C2 – Behavioral or multi-component
C3 – Systemic / best-practice / compliance
C4 – Canonical / boot / certification
```

**P0 RULE:** Any **C2+** claim MUST enter the **recursive loop**.

---

## IV. MODE TRIGGERS

### DEBUG MODE
Triggered by: “fix”, “debug”, “investigate”, “why”, “broken”, “regression”, etc.

### CODE MODE
Triggered by: “write”, “implement”, “refactor”, “add”, “integrate”, etc.

**Both modes are governed identically** once C2+ or external facts are involved.

---

## V. REQUIRED PIPELINE (ALWAYS-ON)

```text
1. MODE SET
2. CLAIM CLASS DECLARED
3. ARTIFACT SCAFFOLD CREATED
4. SEE TRIGGER EVALUATED
5. SEE EXECUTED (if required)
6. ENTER RECURSIVE LOOP
7. TELEMETRY CAPTURE (if runtime behavior exists)
8. MMD CHECK
9. ECL CHECK
10. FINAL DECISION
```

---

## VI. REQUIRED ARTIFACTS (MINIMUM)

### Always Required (C2+)
- SYMPTOM_STATEMENT.md or REQUIREMENTS.md
- DEBUG_HYPOTHESIS_LEDGER.json
- INVARIANT_LIST.md
- ECL_CLAIM_CLASS.json
- PROOF_BUNDLE.md
- MB_RUN_MANIFEST.json
- FINAL_DECISION.json

### Conditionally Required
- SEE_* artifacts (if external facts invoked)
- telemetry/* (if runtime behavior referenced)

**Missing required artifact = BLOCKED or FAIL-CLOSED**

---

## VII. FAILURE STATES (EXPLICIT)

| State | Meaning |
|---|---|
| PASS | Evidence sufficient, claim certified |
| BLOCKED | Missing artifacts or steps |
| FAIL_CLOSED | Protocol violation (e.g., SEE required but not run) |

No other terminal states are allowed.

---

## VIII. FINAL LAW (LOCKED)

```text
LAW OF META BLOOMS DEBUG + CODE (P0)

No non-trivial code or fix may be accepted
without:
- evidence,
- continuity,
- proportional proof,
- and recursive convergence.
```

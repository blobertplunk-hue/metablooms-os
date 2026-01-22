# MetaBlooms Artifact Type Definitions
# Artifact: MB_ARTIFACT_TYPES.md
# Authority: MetaBlooms Core Runtime
# Status: CANONICAL
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## PURPOSE

This document defines the **only valid artifact classes** recognized by MetaBlooms.

Its function is to prevent:
- OS / proof substitution
- Stub artifacts being shipped as runtime systems
- Narrative completion being mistaken for embodiment
- LLM convenience replacing physical reality

Any artifact that violates these definitions is **INVALID BY DEFINITION**.

---

## ARTIFACT CLASSES (EXHAUSTIVE)

### 1. OPERATING SYSTEM (OS)

**Definition**  
A runnable, self-contained system bundle that may be uploaded into a new chat or environment and booted without external assumptions.

**REQUIRED PROPERTIES**
- Contains immutable entrypoint at bundle root:
  - `BOOT_METABLOOMS.py`
- Physically contains all files it claims to use
- Includes module registry and wiring
- Includes governance + enforcement artifacts
- Includes runtime payloads (not references)
- Can fail-closed on invariant violation

**FORBIDDEN**
- Stubs
- Proof-only bundles
- Governance-only bundles
- Historical archives
- "Representative" samples
- Narratives claiming behavior not physically present

**SHIPPING RULE**
If any required property is missing → **MUST NOT BE LABELED OS**

---

### 2. MODULE

**Definition**  
A loadable, unloadable capability unit governed by the Core Runtime Authority.

**REQUIRED PROPERTIES**
- Declared in `MB_MODULE_REGISTRY`
- Explicit activation conditions
- Explicit deactivation/unload semantics
- Declared cost dimensions:
  - cognitive load
  - nondeterminism risk
- No implicit always-on behavior unless declared CORE

**FORBIDDEN**
- Silent activation
- Implicit persistence across tasks
- Side effects without telemetry

**NOTE**
Modules may be shipped *inside* an OS, but are not OSs.

---

### 3. DELTA

**Definition**  
A patch or overlay that modifies an existing OS.

**REQUIRED PROPERTIES**
- Declares base OS compatibility
- Declares mutation scope
- Does not claim standalone executability
- Requires an OS to be meaningful

**FORBIDDEN**
- Being labeled as OS
- Claiming bootability
- Containing entrypoints

---

### 4. PROOF

**Definition**  
Evidence *about* behavior, not behavior itself.

Examples:
- boot traces
- hash receipts
- validation logs
- governance attestations

**REQUIRED PROPERTIES**
- References a specific OS artifact
- Non-runnable
- Non-authoritative

**FORBIDDEN**
- Being shipped as OS
- Being substituted for runtime
- Being used to satisfy delivery requests

---

### 5. STUB

**Definition**  
An incomplete placeholder artifact.

**REQUIRED LABELING**
- Must be explicitly labeled STUB
- Must declare missing components

**FORBIDDEN**
- Accidental shipping
- Renaming as OS, MODULE, or DELTA
- Silent use in place of real artifacts

---

### 6. ARCHIVE (MUSEUM)

**Definition**  
Historical or deprecated artifacts retained for reference only.

**PROPERTIES**
- Non-executable
- Non-authoritative
- Explicitly excluded from runtime resolution

---

## HARD INVARIANTS

- Artifact class **cannot be inferred** from narrative description
- Artifact class is determined **only** by physical contents + this document
- Any ambiguity defaults to **INVALID**
- Proof may support OS acceptance but may never replace OS delivery

---

## ENFORCEMENT

The Core Runtime Authority MUST:
- Reject artifacts whose label does not match contents
- Halt on attempted substitution
- Log violations to telemetry

---

## FINALITY

This document is

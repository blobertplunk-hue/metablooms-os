# MB_ARTIFACT_TYPES.md
MetaBlooms Artifact Classification & Validation Spec
Version: v1.0.0
Status: LOCKED
Depends-On: MB_INVARIANTS.md
Scope: GLOBAL

This document defines the ONLY valid artifact classes in MetaBlooms.
Classification is mechanical, not narrative.

If an artifact does not satisfy its class definition, it MUST be rejected.

---

## ARTIFACT CLASS: OS (Operating System)

### Definition
An OS is a **bootable runtime system** capable of executing MetaBlooms logic
without relying on chat context, explanation, or external narrative.

### REQUIRED PROPERTIES (ALL MANDATORY)

1. **Entrypoint**
   - A real, executable file
   - Fixed name (canonical)
   - Discoverable at bundle root
   - May not be simulated, stubbed, or implied

2. **Runtime Payload**
   - Executable logic beyond governance
   - Module loader or dispatcher
   - State initialization logic

3. **Boot Verifiability**
   - Boot path can be inspected mechanically
   - Failure conditions halt execution
   - No text-only "boot success" claims allowed

4. **Manifest**
   - Enumerates all runtime components
   - Identifies modules, deltas, configs
   - Used by validators

### EXPLICITLY NOT AN OS

- Governance-only bundles
- Proof bundles
- Specs
- Stubs
- ZIPs that "should boot"
- Anything requiring explanation to justify bootability

---

## ARTIFACT CLASS: MODULE

### Definition
A Module is a **self-contained capability** that can be loaded, unloaded,
validated, and versioned independently.

### REQUIRED PROPERTIES

1. **Contract**
   - Explicit inputs
   - Explicit outputs
   - Explicit failure modes

2. **Isolation**
   - No implicit dependency on other modules
   - All dependencies declared

3. **Registration**
   - Appears in a module registry
   - Addressable by ID

4. **Load Semantics**
   - Can be activated or deactivated
   - Does not rely on chat memory

### INVALID MODULES

- "Background behavior"
- "Always-on logic" without registration
- Capabilities implied by naming
- Tools that only exist in explanation

---

## ARTIFACT CLASS: DELTA

### Definition
A Delta is a **bounded change set** that modifies one or more artifacts
WITHOUT redefining them.

### REQUIRED PROPERTIES

1. **Target**
   - Explicit artifact(s) affected

2. **Operation**
   - Add / Remove / Modify (explicit)
   - No ambiguous "update" language

3. **Preconditions**
   - What must exist before application

4. **Postconditions**
   - What must be true after application

5. **Reversibility Declaration**
   - Reversible / Irreversible (explicit)

### INVALID DELTAS

- "Latest version"
- "Full replacement" without manifest
- Narrative change descriptions
- Deltas that silently bundle artifacts

---

## ARTIFACT CLASS: PROOF

### Definition
A Proof is **evidence about behavior**, not behavior itself.

### REQUIRED PROPERTIES

1. **Claim**
   - What behavior is being evidenced

2. **Method**
   - How evidence was produced

3. **Scope**
   - What the proof applies to
   - What it does NOT apply to

4. **Non-Authority**
   - Proof cannot enable behavior
   - Proof cannot substitute for runtime

### COMMON MISUSE (FORBIDDEN)

- Shipping proof as OS
- Treating logs as enforcement
- Using proof to justify missing code

---

## ARTIFACT CLASS: SPEC

### Definition
A Spec defines **constraints, rules, or contracts** that other artifacts must obey.

### REQUIRED PROPERTIES

1. **Scope**
   - What artifacts are governed

2. **Enforcement Point**
   - Who or what enforces the spec

3. **Violation Handling**
   - What happens on failure

### NON-ENFORCEABLE SPECS

Specs without enforcement logic are informational ONLY
and may not be treated as governance.

---

## ARTIFACT CLASS: REGISTRY (SPECIAL)

### Definition
A Registry is a **mapping artifact** that connects identifiers to artifacts.

### REQUIRED PROPERTIES

- Deterministic resolution
- No narrative fallbacks
- Must be machine-readable

Registries are REQUIRED for:
- Modules
- Deltas
- Entry points
- Telemetry hooks

---

## CLASSIFICATION RULE (OVERRIDING)

If an artifact satisfies multiple class definitions,
it MUST be split.

Hybrid artifacts are forbidden.

---

## FAILURE MODE

If classification fails:
- Artifact is rejected
- Downstream artifacts halt
- No substitution permitted

---

## END OF SPEC

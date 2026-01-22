# MetaBlooms Module Registry
# Artifact: MB_MODULE_REGISTRY.md
# Authority Level: CORE (subordinate to CRA)
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## PURPOSE

The **Module Registry** is the only authoritative source of truth for:

- what modules exist
- what state they are in
- whether they are loadable
- whether they are active
- why they are active

If a module is not registered here, **it does not exist**.

Conversation memory does not count.
Past OS bundles do not count.
Intent does not count.

---

## DEFINITIONS

### MODULE

A **module** is:
- a discrete capability
- loadable and unloadable
- independently testable
- inert unless activated

Modules are **not** features.
Modules are **not** ideas.
Modules are **not** folders that "seem important."

---

## REGISTRY FORMAT

Each module entry MUST include all fields below.

### REQUIRED FIELDS

```yaml
module_id:            # unique, immutable identifier
display_name:         # human-readable name
version:              # semantic version
status:               # one of: REGISTERED | VALIDATED | ACTIVE | DISABLED | ARCHIVED
artifact_path:        # physical path inside OS bundle
entrypoint:           # callable entrypoint (file:function)
dependencies:         # explicit list (may be empty)
activation_conditions:# explicit triggers
deactivation_rules:   # how/when module unloads
telemetry_hooks:      # what it reports
validation_checks:    # how correctness is proven
last_verified:        # timestamp
authority:            # who registered it (CRA reference)
notes:                # optional, non-authoritative


---

## REGISTERED MODULES


### SDI-02 (Student Diagnostic Intelligence)

```yaml
module_id: SDI-02
display_name: Student Diagnostic Intelligence (i-Ready → STAAR)
version: "1.1"
status: ACTIVE
artifact_path: modules/sdi02/SDI-02_v1.1_MODULE_VALIDATOR_WIRED.md
entrypoint: modules.sdi02:SDI-02 (spec-driven; see artifact)
dependencies:
  - SDI-02-VAL@1.0
activation_conditions:
  - User provides i-Ready BOY+MOY diagnostics and requests SDI/STAAR grouping or synthesis
deactivation_rules:
  - If required inputs missing → HALT (fail-closed)
telemetry_hooks:
  - none (chat-environment)
validation_checks:
  - SDI-02-VAL gates G0–G6 must PASS with a Run Manifest JSON
last_verified: "2026-01-10T21:26:30Z"
authority: CRA (MetaBlooms)
notes: "Validator-wired. Completion requires SDI-02-VAL PASS. Includes invocation + schema + runner."
```

### SDI-02-VAL (Compliance Validator)

```yaml
module_id: SDI-02-VAL
display_name: SDI-02 Compliance Validator
version: "1.0"
status: ACTIVE
artifact_path: modules/sdi02/SDI-02-VAL_v1.0.md
entrypoint: modules.sdi02.run_validator:main
dependencies: []
activation_conditions:
  - Invoked as Stage 8 gate for SDI-02 runs
deactivation_rules:
  - none
telemetry_hooks:
  - none (chat-environment)
validation_checks:
  - Run Manifest schema validation + gate PASS/FAIL evaluation
last_verified: "2026-01-10T21:26:30Z"
authority: CRA (MetaBlooms)
notes: "Hard gate: SDI-02 cannot complete unless SDI-02-VAL passes."
```

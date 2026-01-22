# MetaBlooms Delta Protocol
# Artifact: MB_DELTA_PROTOCOL.md
# Authority Level: CORE (subordinate to CRA)
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## PURPOSE

The **Delta Protocol** defines the *only* legal way MetaBlooms may change.

If a change:
- is not a Delta
- is not registered
- is not applied
- is not recorded

…it **did not happen**, no matter how many chats discussed it.

This protocol is the mechanical bridge between:
- decisions
- artifacts
- shipped OS bundles

---

## DEFINITIONS

### DELTA

A **Delta** is a self-contained, explicit, reviewable change package that:

- adds, modifies, or removes artifacts
- declares its scope and dependencies
- can be applied deterministically
- can be rolled back
- leaves an audit trail

Conversation is *not* a Delta.
Intent is *not* a Delta.
Narrative agreement is *not* a Delta.

---

## DELTA TYPES

### STRUCTURAL
- new modules
- new registries
- new enforcement layers
- new entrypoints

### BEHAVIORAL
- activation rules
- sequencing changes
- governance logic
- validation logic

### DOCUMENTARY
- doctrines
- contracts
- invariants
- protocols

### REMOVAL
- deprecations
- pruning
- archival

---

## REQUIRED DELTA CONTENTS

Every Delta MUST contain:

```yaml
delta_id:            # unique, immutable
title:               # human-readable
type:                # one of the DELTA TYPES
version:             # semantic
author:              # authority reference
timestamp:           # creation time
scope:               # what it touches
dependencies:        # other deltas required
adds:                # new files/modules
modifies:            # files/modules changed
removes:             # files/modules removed
validation_steps:    # how correctness is proven
rollback_plan:       # how to undo safely

# MetaBlooms Boot Contract
# Artifact: MB_BOOT_CONTRACT.md
# Authority Level: CORE (supersedes narrative claims)
# Compression Level: NONE (NON-COMPRESSIBLE)

---

## PURPOSE

This contract defines what it means for a MetaBlooms artifact to be called:

- an OS
- bootable
- canonical
- shippable

Anything that violates this contract **is not an OS**, regardless of intent, documentation, or prior usage.

---

## DEFINITIONS

### OS (Operating System)

An artifact may only be called a **MetaBlooms OS** if it:

1. Is a single distributable bundle
2. Contains an immutable entrypoint
3. Executes a real boot sequence
4. Enforces governance before execution
5. Fails closed on violation
6. Leaves an evidence trail

If any condition is unmet → it is NOT an OS.

---

## IMMUTABLE ENTRYPOINT REQUIREMENT

Every OS bundle MUST contain, at its root:

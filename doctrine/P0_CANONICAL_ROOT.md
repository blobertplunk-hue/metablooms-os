# P0.CANONICAL_ROOT.ENFORCEMENT

## Definition
MetaBlooms has exactly one canonical OS runtime root:

- `/mnt/data/MetaBlooms_OS`

ZIP artifacts are immutable inputs/exports only. Runtime state must never be written into ZIPs.

## Rules (Fail-Closed)
- Exactly one canonical OS root under `/mnt/data`.
- All writes must resolve under the canonical root (`realpath` must start with canonical root realpath + path separator).
- Missing canonical root → BOOT FAIL.
- Ambiguous canonical root → BOOT FAIL.
- Write escape outside canonical root → FATAL HALT.

## Enforcement Surface
- `runtime/canonical_root.py` provides canonical root resolution and write-path guards.
- `validators/validate_canonical_root_v1.py` must run at boot and must fail closed.

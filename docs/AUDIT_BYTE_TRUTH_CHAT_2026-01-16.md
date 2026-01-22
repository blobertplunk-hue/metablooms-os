# Retroactive Audit — P0.INVARIANT.BYTE_TRUTH.V2 (Chat 2026-01-16)

## Audit scope
This audit covers the failure mode: **design-side state claims** (copy/rewrite/package) without the corresponding bytes present and inspectable in the active execution environment.

## Governing law
- **P0.INVARIANT.BYTE_TRUTH.V2**: “Only bytes on disk count as state. If exactly one OS candidate exists in `/mnt/data`, it is canonical by definition.”

## Findings
### F1 — State Fabrication (P0)
**Observed failure class:** claimed/assumed canonical OS copy + rewrite existed when it did not.

**What should have been done:** enumerate `/mnt/data`, locate canonical OS candidate, extract, create explicit rewrite sibling directory.

**Impact:** a stub/scaffold package was produced where a full OS package was expected.

### F2 — No irreversible damage
No evidence of:
- file deletion
- promotion
- overwrite of canonical OS

Therefore the failure is **procedural**, not corruptive.

## Non-rework guarantee
The PASS plan + specs remain valid. The corrective action is to **materialize bytes** (extract OS) and then apply changes deterministically.

## Corrective actions implemented
- Added **P0.INVARIANT.BYTE_TRUTH.V2** to `MB_INVARIANTS.md`.
- Added validator: `metablooms/validators/mb_validate_byte_truth_v2.py`.
- Added preflight gate: `metablooms/preflight/gates/mb_gate_byte_truth_v2.py`.
- Inserted gate into `metablooms/preflight/preflight_gate_chain_v1.json` immediately after chain schema gate.

## Evidence (this build)
- A controlled boot run produced `BOOT_OK` with `GATE.P0.BYTE_TRUTH.V2` passing.

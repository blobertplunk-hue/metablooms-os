# MetaBlooms Boot Repair Log — 2026-01-17

Scope: Repair boot failures encountered when executing `BOOT_METABLOOMS.py` from the bundle
`MetaBlooms_OS_PASS3_PLUS_SHIPPING_PROCEDURE_V1.zip`.

## Evidence Summary

- Entrypoint: `BOOT_METABLOOMS.py` (unchanged)
- Runner: `RUN_METABLOOMS.py` (patched for schema + call-arity compatibility)
- Boot result after repair: `BOOT_OK` with exit code 0

## Root Causes

1. **Gate chain JSON schema mismatch**
   - `preflight_gate_chain_v1.json` shipped as a **bare list** but multiple consumers assumed a dict wrapper `{"gates": [...]}`.

2. **Gate callable arity mismatch**
   - Some gates expose `run_gate(context)` while the runner always called `run_gate(context, ledger_writer)`.

3. **Mixed gate id keys**
   - A gate entry used `gate_id` instead of `id`, triggering the schema gate.

4. **P0 NO_PLACEHOLDERS failure**
   - `runtime/workspace.py` and `runtime/tool_facade.py` were silent stubs (`class X: pass`).

## Repairs Applied (Append-Only Discipline)

Backups created alongside each modified file (suffix: `.bak_2026-01-17`).

### A) Runner schema + arity hardening
- File: `RUN_METABLOOMS.py`
  - `_load_chain()` now accepts both:
    - bare list `[...]`
    - wrapper dict `{ "gates": [...] }`
  - Gate invocation now uses deterministic signature inspection to call either:
    - `fn(context)`
    - `fn(context, None)`
  - Result normalization now accepts either `ok` or `pass` keys.
  - Boot context now supplies `root`, `os_root`, and `zroot`.

### B) Missing-middle detector compatibility
- File: `metablooms/validators/missing_middle_detector_v1.py`
  - `_detect_gate_chain_registration()` now accepts chain as list or dict wrapper.

### C) Chain schema gate compatibility
- File: `metablooms/preflight/gates/mb_gate_preflight_chain_schema_v1.py`
  - `_checks()` now accepts chain as list or dict wrapper.

### D) Normalize gate chain id key
- File: `metablooms/preflight/preflight_gate_chain_v1.json`
  - Converted the single `gate_id` entry to `id`.

### E) Remove runtime silent stubs
- Files:
  - `runtime/workspace.py`
  - `runtime/tool_facade.py`
  - Replaced silent stubs with minimal functional implementations.

## Boot Evidence

- Command: `python BOOT_METABLOOMS.py`
- Exit code: `0`
- Tail output: `BOOT_OK`

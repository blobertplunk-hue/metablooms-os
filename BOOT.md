# MetaBlooms Boot Contract (Authoritative)

## ZOOP Invariant (MANDATORY)

If the authoritative OS artifact is packaged (ZIP):
1. ZOOP (extract to runtime filesystem) MUST occur first.
2. Entry-point discovery is illegal prior to ZOOP.
3. After ZOOP, the runtime root is authoritative for:
   - BOOT_METABLOOMS.py
   - boot_manifest.json
   - ledgers, registries, and modules

Failure to ZOOP before evaluation is a contract violation.

---
This file exists solely to grant authority to extract and evaluate the packaged OS.

## CTOS Boot Gates — Quality Gate (Gate 2)

MetaBlooms CTOS boot is gated by **Q0 v1.1 (Best‑Per‑Atom Quality Gate)**.

- The authoritative checklist is: `spec/ctos/BOOT_COMPLIANCE_CHECKLIST_CTOS_v2_1.md`
- **Gate 2 is REQUIRED** for non‑trivial code generation:
  - multi‑candidate selection (or valid triviality exemption)
  - rubric registry loaded (`spec/ctos/metablooms_rubrics.json`)
  - thresholds satisfied
  - unresolved `QUALITY_GATE_*` failures block boot

Failure mapping:
- `BOOT_FAILED: QUALITY_GATE_BLOCKED`
- `BOOT_FAILED: QUALITY_GATE_FAILED`

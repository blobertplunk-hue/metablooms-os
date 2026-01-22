# SHIP SCOPE & INVARIANTS — MetaBlooms OS v1_3_12_LEDGERVERIFYFIX
Date: 2026-01-08
Ship intent: A (ship even if K incomplete; label honestly)

## Included
- Immutable entrypoint: BOOT_METABLOOMS.py
- boot_manifest.json
- ledger subsystem (ledger/ledger.ndjson)
- RIDIE kernel integration specs + persistence delta + promotion autowire + telemetry spec (as artifacts present in /mnt/data, included here in /evidence)
- Kindergarten ELAR work products present in this bundle (if any)

## Explicitly Incomplete / Labeled Scaffold
- K ELAR frames beyond K.4 are not fully decompressed with verbatim TEA text.
- Grades 1–12 ELAR/SLAR not included as canonical content.

## Invariants
- Canonical content is immutable; derived views are labeled and reversible.
- RIDIE cannot mutate canonical artifacts; only emits proposals.
- Process rules change only via promotion gate and are ledgered.
- Fail-closed on ambiguity: boot proof requires LEDGER_VERIFY ok:true.

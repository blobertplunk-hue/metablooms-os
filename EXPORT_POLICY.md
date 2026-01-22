# EXPORT_POLICY



## Phase G: Artifact Latest/Best Resolution (MANDATORY)
Before shipping any cumulative OS ZIP, you MUST generate and validate `LATEST.json` using the resolver:

- Run: `python tools/artifact_resolver_latest_best.py <artifact_directory>`
- Require outputs:
  - `LATEST.json`
  - `latest_best_proof.json`
- Require that `LATEST.json.best_os_zip` points to a boot-verified OS ZIP with a matching `.sha256`.

If any requirement fails: **FAIL-CLOSED** (do not ship).


## Phase G: ZOOP–BOOT Pairing Proof (MANDATORY)
Before shipping any OS bundle, Phase G MUST include BOTH:

1) Negative assertion (expected fail):
   - Extract bundle to disposable workspace
   - Run BOOT_METABLOOMS.py WITHOUT running ZOOP_METABLOOMS.py
   - REQUIRE: BOOT_FAILED: ZOOP_REQUIRED and a ledgered BOOT FAIL

2) Positive assertion (expected pass):
   - Run ZOOP_METABLOOMS.py
   - Verify receipt + ledger event_id match
   - Run BOOT_METABLOOMS.py
   - REQUIRE: BOOT_OK and all required validators OK

Export is FAIL-CLOSED if either assertion is missing or produces the wrong outcome.

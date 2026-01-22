# MetaBlooms DeltaPack: MB_P0_RESEARCH_MATERIALIZER_V1

## Purpose
Add automatic `claim.created_ts` injection at claim-generation time and correct research lifecycle gate ordering.

## Payload
- Added:
  - `metablooms_runtime/invariants/research_materializer.py`
  - `metablooms_live/runtime/research_claims.py`
- Modified:
  - `metablooms_live/runtime/gate_runner.py`
  - `metablooms_live/runtime/runtime_entrypoint.py`

## Apply procedure (local / sandbox / other chat)
1. Unzip your target MetaBlooms OS bundle to a working directory.
2. Copy the `payload/` folder contents into the OS root, overwriting existing files where paths match.
3. Run your canonical packaging step to re-zip the OS.
4. Run boot/acceptance checks.

## Acceptance checks (minimum)
- A RESEARCH-required run creates/normalizes:
  - `research/claims.json` with `claim_id` and `created_ts` for every claim entry
  - `research/citation_map.json` with `bindings` list
- Gate ordering:
  - Preflight runs `research_materializer` before evidence/binding enforcement.
  - Postflight enforces research receipts + citation coverage + claim↔receipt↔timestamp binding + staging commit.
- Runtime entrypoint sets: `context["runtime_entrypoint"] = True`.

## Fail-closed expectations
- The materializer does NOT fabricate Sandcrawler receipts.
- If receipts/citations are missing postflight, the system must still fail-closed.

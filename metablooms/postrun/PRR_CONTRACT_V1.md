# Post-Run Review (PRR) Contract v1

## Purpose
PRR is a deterministic **after-action review** layer that runs *after* a governed MetaBlooms run (boot/apply/ship) and produces:
1) a structured **Retrospective Report**
2) a set of **Minimal Mutation Tickets (MMTs)** (small, safe, high-leverage improvements)
3) optional **autofix candidates** (safe, mechanical fixes)

PRR is designed to make improvements **persist** without relying on memory or manual prompting.

## Inputs (canonical)
PRR consumes whichever of the following exist for the run:
- `Evidence Log v2` (markdown)
- `ledger/ledger.ndjson` (append-only)
- `docs/DIFF_MANIFEST.md` or `diff manifest` artifacts
- `preflight` outputs (gate events in ledger)
- `tool outputs` if referenced by the Evidence Log

## Outputs (canonical)
PRR MUST emit:
- `postrun/prr_report_v1.json`
- `postrun/mmt_queue_v1.json`
- `postrun/prr_summary_v1.md`

## Determinism requirements
- PRR MUST NOT invent files or claims that are not supported by inputs.
- PRR MAY infer improvements, but must label them as `inference` and cite which evidence lines/fields support them.
- PRR MUST produce stable IDs for tickets and findings (hash-based).

## MMT rules
Each MMT MUST be:
- small scope (single responsibility)
- low risk (no behavior changes without tests)
- explicitly tied to a failure signal or friction signal

MMT required fields:
- `mmt_id` (stable)
- `phase` (Design|Build|Gate|Ship|Boot|Docs)
- `problem`
- `proposal`
- `expected_gain`
- `risk`
- `status` (Proposed|Accepted|Rejected|Done)
- `evidence_refs` (pointers into Evidence Log / ledger)

## Failure signals (v1 taxonomy)
- `TRUNCATION_RISK`
- `AMBIGUITY_LOOP`
- `MISSING_AUTHORITY`
- `MISSING_CANONICAL_FILE`
- `NONDETERMINISTIC_IO`
- `UNVERIFIED_EXECUTION_CLAIM`
- `DOWNLOAD_LINK_FAILURE`

## Friction signals (v1 taxonomy)
- `TOO_MANY_TURNS`
- `USER_REPEAT_PROMPT`
- `MANUAL_INVOKE_REQUIRED`

## Automation
PRR is allowed to suggest (and optionally apply) autofixes only when:
- the fix is mechanical
- bounded to definitions or registry wiring
- reversible
- emits a ChangeSet + Evidence Log update


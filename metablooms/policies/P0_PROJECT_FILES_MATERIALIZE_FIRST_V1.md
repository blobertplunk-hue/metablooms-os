# P0 Policy: Project Files Materialize-First (V1)

## Rule
When Project Files contain an OS bundle or required artifacts, the system MUST attempt materialization into the sandbox workspace (`/mnt/data`) before:
- asking the user to re-upload
- declaring missing bytes
- switching to chunked transport
- answering OS existence/location questions

## Required Evidence (bytes)
The system MUST write a breadcrumb at:
- `metablooms/diagnostics/materialization_breadcrumb_v1.json`

The breadcrumb MUST include:
- `schema`, `ts`, `source`, `target`, `outcome`
- If `outcome=FAILED`, include `reason`

## Fail-closed
If the breadcrumb is missing, the system is in violation and MUST BLOCK.

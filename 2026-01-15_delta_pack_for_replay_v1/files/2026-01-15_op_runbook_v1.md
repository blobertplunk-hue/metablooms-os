# MetaBlooms Operation Runbook v1

## Objective
Prevent ambiguous outcomes by enforcing a deterministic, evidence-backed workflow.

## Rules
- Write any non-trivial script to disk before running it.
- Redirect stdout and stderr to on-disk log files.
- Use a staging directory for installs/deltas, then promote via atomic rename.
- Write an append-only ledger entry for every operation.

## Required evidence per operation
- Operation ID
- Inputs (paths, filenames)
- Output paths
- SHA256 of inputs and key outputs
- Exit code
- Captured stdout log path
- Captured stderr log path
- Pass/fail status

## Anti-truncation tactics
- Prefer compact summaries in chat; store full logs on disk.
- When listing directories, use targeted listings (top-level only) and provide a tree on request.

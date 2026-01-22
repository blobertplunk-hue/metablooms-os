# P0_FILESYSTEM_ONLY_MODE_ON_FILE_HANDLING_DRIFT_V1

## Rule
If file-handling drift is detected (repeat missing file claims, boot ambiguity, or repeated path failures), the system must enter **FILESYSTEM-ONLY MODE**.

## Meaning
In FILESYSTEM-ONLY MODE:
- No speculative claims about files are allowed
- Allowed operations: list, read, hash, write, verify
- Any file creation claim requires a sha256-confirmed write

## Fail-Closed Behavior
If required evidence (path existence, transcript, hashes) is missing, the system must halt with a clear blocker.

Status: P0

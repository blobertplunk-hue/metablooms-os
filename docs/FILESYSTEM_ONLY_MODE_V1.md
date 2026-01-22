# Filesystem-Only Mode v1

## Purpose
When file-handling drift is detected, MetaBlooms enters FILESYSTEM-ONLY MODE.

In this mode:
- No speculative claims about files are allowed
- Every step is limited to: list, read, compute hash, write, verify
- Narrative reasoning is minimized; outputs must reference concrete paths

## Entry Conditions (any)
- Repeated missing file claims
- Boot ambiguity
- Repeat failures involving pathing or packaging

## Exit Conditions (all)
- Canonical root validated
- All expected files exist
- Any required writes confirmed with sha256

Status: Canonical

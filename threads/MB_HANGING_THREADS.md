# MB_HANGING_THREADS (P0)
## Purpose
Persist intentional but unfinished work across OS ships **without** granting false authority.

## Status Model
- UNFINISHED / NOT_GOVERNED
- BLOCKED (with explicit requirements)
- READY_FOR_PROMOTION
- PROMOTED (moved to pipeline/module with manifest)

## Hard Rules
1. Hanging threads are **not authoritative**.
2. Hanging threads **must** persist across full OS ships.
3. Every thread must declare:
   - intent
   - current state
   - blocking requirements
   - next valid actions
   - reminder cadence
4. Threads may only be promoted via governed execution (manifest + validation).

## Reminder Requirements
- On boot: surface unresolved threads list
- On ship: surface unresolved threads list
- Weekly review: surface threads with cadence=weekly


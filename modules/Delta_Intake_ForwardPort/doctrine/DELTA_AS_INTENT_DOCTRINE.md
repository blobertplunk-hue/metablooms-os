# Doctrine: Delta as Intent (not patch)

In MetaBlooms, deltas may originate from:
- older OS lines
- parallel chats
- external skill packs

Therefore:
1) A delta is interpreted as INTENT + SCOPE + EXPECTED OUTPUTS.
2) The system generates a FORWARDPORT_PLAN against the current OS.
3) The system emits receipts and a diff, then produces a new full OS bundle.

This prevents "apply-as-is" corruption and supports convergent evolution across branches.

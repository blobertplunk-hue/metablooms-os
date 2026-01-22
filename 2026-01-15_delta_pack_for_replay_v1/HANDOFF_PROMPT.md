Handoff Prompt (Replay v1)

Use this prompt in a new chat with the target MetaBlooms OS ZIP already mounted in /mnt/data, along with this delta pack ZIP.

Prompt:

"""
Proceed fail-closed.

1) Extract this delta pack ZIP.
2) Read 2026-01-15_metablooms_os_mount_spec_v1.md and enforce the canonical tree install model:
   - Install the target OS into /mnt/data/MetaBlooms/zroot using staging + atomic swap.
   - Ensure /mnt/data/MetaBlooms_OS is a symlink to /mnt/data/MetaBlooms/zroot.
   - Write an install ledger entry under /mnt/data/MetaBlooms/installs/.
3) Adopt the ledger-backed operations discipline in 2026-01-15_op_runbook_v1.md for all subsequent operations.
4) Transactionally apply DELTA_2026-01-15_LEARNING_GOVERNANCE_LOCKIN.zip into /mnt/data/MetaBlooms/zroot with an append-only apply ledger.
5) Run preflight and boot against /mnt/data/MetaBlooms_OS.

Return:
- full apply manifest (paths + hashes)
- boot/preflight logs paths
- updated OS ZIP export (optional)
"""

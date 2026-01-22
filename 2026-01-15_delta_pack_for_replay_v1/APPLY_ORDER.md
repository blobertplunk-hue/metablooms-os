MetaBlooms Delta Pack (Replay v1)

Goal
- Provide a deterministic, fail-closed, evidence-backed way to reproduce the improvements from the 2026-01-15 chat in another MetaBlooms OS lineage.

Scope
- This pack contains:
  (1) the Learning Governance Lock-In delta ZIP (functional governance changes)
  (2) the canonical OS tree + install model specification (mount spec)
  (3) the ledger-backed operations discipline runbook (op runbook)
  (4) a manifest describing prerequisites + apply order

Non-goals
- This pack does NOT include the entire base OS.
- This pack does NOT attempt to modify the immutable entrypoint contract.

Prerequisites (P0)
- Target OS bundle must contain BOOT_METABLOOMS.py at its canonical root.
- Target OS must have (or accept) a canonical tree install model:
  /mnt/data/MetaBlooms/{zroot,bundles,installs,logs,artifacts}
- Target OS must have a preflight/boot chain that can be invoked from the canonical root.

Apply Order (Fail-Closed)
1) Enforce/install canonical tree model (per mount spec):
   - Install the target OS into /mnt/data/MetaBlooms/zroot using staging + atomic swap
   - Ensure /mnt/data/MetaBlooms_OS is a symlink to /mnt/data/MetaBlooms/zroot
   - Write an install ledger entry under /mnt/data/MetaBlooms/installs/

2) Enforce ledger-backed operation discipline (per op runbook):
   - For each operation, create an OP_ID-scoped directory
   - Persist stdout/stderr/exitcode + op.json inputs
   - Use ledger as the source of truth; logs are diagnostic only

3) Apply functional delta ZIP:
   - DELTA_2026-01-15_LEARNING_GOVERNANCE_LOCKIN.zip
   - Apply transactionally (stage → validate → sync → atomic swap if applicable)
   - Write an apply ledger entry with file hashes + conflict policy + results

4) Run preflight + boot from canonical root:
   - Root: /mnt/data/MetaBlooms_OS (symlink)
   - Entrypoint: /mnt/data/MetaBlooms_OS/BOOT_METABLOOMS.py
   - Fail-closed on any P0 gate failure

Suggested Conflict Policy
- Default: fail-closed on any file collision unless the delta explicitly declares precedence.

Artifacts to produce in the target OS
- /mnt/data/MetaBlooms/installs/<timestamp>_install.json
- /mnt/data/MetaBlooms/installs/<timestamp>_delta_apply.json
- /mnt/data/MetaBlooms/logs/<op_id>/{stdout.txt,stderr.txt,exitcode.txt}

# MetaBlooms Skill Runtime

A “skill” is a directory containing:
- SKILL.md (required): purpose, triggers, IO contract, progressive disclosure links
- metadata.json (optional)
- scripts/ (optional)
- data/ (optional)

MetaBlooms rules:
- A skill must declare: Trigger, Inputs, Outputs, Constraints.
- Any skill that calls web.run must require citations.
- Skills are indexed into SEGMENT_INDEX.json under `skills`.

Receipts:
- SKILL_RECEIPT.json emitted per run (inputs hashes, outputs hashes, authority label).

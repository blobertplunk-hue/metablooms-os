# CSF Boot Integration Spec v1

Boot hook responsibilities (opt-in):
- Discover skills under modules/Claude_Skills_Factory/skills
- Validate each SKILL.md against Skill Validator
- In P0_STRICT mode: fail-closed if required skills missing/invalid
- Emit CSF_BOOT_REPORT.json

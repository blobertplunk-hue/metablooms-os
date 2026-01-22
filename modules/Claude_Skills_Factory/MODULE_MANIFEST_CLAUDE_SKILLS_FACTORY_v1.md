# Claude Skills Factory (CSF) — Module Manifest v1

Purpose: Provide a MetaBlooms-native “skills” substrate inspired by Claude skills-style progressive disclosure.
This module turns skill repos (SKILL.md + optional scripts/data) into **callable, governed MetaBlooms segments**.

Status: Registered, disabled by default. Enable via MB_RUNTIME_CONFIG.json:
```json
{"modules":{"claude_skills_factory":{"enabled":true,"mode":"P0_WARN"}}}
```

Modes:
- DISABLED: no-op
- P0_WARN: logs violations, continues
- P0_STRICT: fail-closed on missing/invalid required skills

Surfaces:
- BOOT hook (optional checks)
- Pipeline invocation (skill selection)
- Runtime execution (skill-run receipts)

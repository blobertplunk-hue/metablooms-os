# EVIDENCE_ENGINE (P0)

Rule: Any request that could benefit from up-to-date or niche information must route through EVIDENCE_ENGINE.

Fail-closed:
- If EVIDENCE_ENGINE cannot be invoked, do not approximate.
- Ask for clarification or declare EXECUTION_BLOCKED with reason.

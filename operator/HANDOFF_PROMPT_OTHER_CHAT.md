# Handoff Prompt (Other Chat) — Apply ROW + Pipeline Mapping

You are receiving a delta defining:
- Pipeline registry (P0..P9)
- Pipe section schema (S0..S5)
- ROW routing table for common intents

Instructions:
1) Treat /contracts files as canonical.
2) When the user says "Start a ROW: <INTENT>", route deterministically using ROW_ROUTING_TABLE.json.
3) Enforce fail-closed behavior when intent is ambiguous.
4) Do not claim execution without evidence.

Minimum output each time:
- Print the resolved routing decision (ACTIVE/AUTO/DEFER/SLEEP).

# Runtime Wiring (P0)

Validators are invoked in this order:
1) validate_pipeline_invocation
2) validate_phase_transition
3) validate_evidence_gate
4) validate_promotion (when applicable)
5) validate_reminder_policy (on BOOT/SHIP)

Any failure => FAIL_CLOSED with classified reason.

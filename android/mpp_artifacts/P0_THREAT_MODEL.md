# P0 THREAT_MODEL — QuickUpload Tier B

## Assets
- GitHub access token (highest sensitivity)
- Local files (confidentiality + integrity)
- Repo integrity (no unintended overwrites, no secret commits)
- Audit logs (must not leak secrets)

## Threats → Mitigations

| Threat | Mitigation |
|--------|-----------|
| Token leakage in logs/UI | Strict redaction, never print tokens, structured logs with allowlist fields |
| Token theft at rest | Store only in encrypted storage/Keystore; prefer device flow tokens; support revoke flow |
| Accidental overwrite (wrong path/branch) | Preflight diff, show destination path clearly, require confirmation, safe default = create new |
| Branch protection / perms cause silent failure | Detect 403/404 patterns and explain; GitHub often returns 404 for permission reasons |
| Network tampering / MITM | HTTPS + system trust store; pinning optional |
| Large file upload failure | Size gating + explicit strategy (LFS or alternate flow) |

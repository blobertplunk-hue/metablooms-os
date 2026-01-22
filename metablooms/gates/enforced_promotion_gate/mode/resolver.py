def resolve_mode(requested_mode: str | None, target_channel: str) -> str:
    '''
    Minimal Mode Resolver:
      - Default STRICT
      - If target is CANONICAL or TRUSTED, only STRICT is allowed in this demo
    '''
    effective = requested_mode or "STRICT"
    if target_channel in ("CANONICAL", "TRUSTED") and effective != "STRICT":
        # Fail-closed designs can BLOCK; this demo forces STRICT.
        effective = "STRICT"
    return effective

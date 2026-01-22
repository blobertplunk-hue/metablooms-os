from metablooms.runtime.turn_lock import acquire_turn_lock

def run_gate(ctx):
    # Policy-driven stale threshold (seconds)
    stale_after_s = getattr(ctx, "lock_stale_after_s", 900)
    acquire_turn_lock(ctx.os_root, ctx.turn_id, stale_after_s=stale_after_s)

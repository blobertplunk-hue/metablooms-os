
from pathlib import Path
from metablooms.state.snapshot_writer import write_snapshot
from metablooms.state.delta_pruner import prune_deltas

def snapshot_and_prune_if_due(ctx):
    """
    Snapshot cadence hook.
    Takes snapshot every N turns (ctx.snapshot_interval).
    After snapshot, prune deltas.
    """
    turn_index = ctx.turn_index
    if turn_index % ctx.snapshot_interval != 0:
        return None

    snapshot_path = write_snapshot(
        os_root=ctx.os_root,
        turn_id=ctx.turn_id,
        materialized_state=ctx.materialized_state
    )

    removed = prune_deltas(ctx.os_root, keep_last=ctx.delta_keep_last)

    return {
        "snapshot": str(snapshot_path),
        "deltas_pruned": [str(p) for p in removed]
    }

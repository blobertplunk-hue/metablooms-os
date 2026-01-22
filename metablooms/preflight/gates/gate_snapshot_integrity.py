from metablooms.runtime.snapshot_verify import find_latest_snapshot, verify_snapshot_file

def run_gate(ctx):
    snap = find_latest_snapshot(ctx.os_root)
    if snap is None:
        return
    verify_snapshot_file(snap)

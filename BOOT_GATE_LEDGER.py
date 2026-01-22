# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_LEDGER.py
import os

def gate(ledger_dir):
    assert os.path.exists(ledger_dir), "Ledger path missing"
    assert os.access(ledger_dir, os.W_OK), "Ledger not writable"

    # Activate Intuition Finch Runtime (fail-closed): write initial Selection Record.
    # BOOT_METABLOOMS passes the ledger *directory* (ROOT/ledger).
    root_dir = os.path.abspath(os.path.join(os.path.dirname(ledger_dir), ".")) if os.path.isdir(ledger_dir) else os.path.abspath(os.path.join(os.path.dirname(ledger_dir), os.pardir))
    try:
        from modules.intuition_finch_runtime.runtime.env_sense import sense_environment
        from modules.intuition_finch_runtime.runtime.finch_select import select_finch
        from modules.intuition_finch_runtime.runtime.selection_record import write_selection_record
        ev = sense_environment()
        finch = select_finch(ev)
        write_selection_record(root_dir, ev, finch, note="boot_activation")
    except Exception as e:
        raise AssertionError(f"Intuition runtime activation failed: {e}")

    return True

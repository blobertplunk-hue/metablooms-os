# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

# BOOT_GATE_INTUITION_RUNTIME.py
# Activates the Intuition Finch Runtime at boot by writing an initial Selection Record.
# Fail-closed: if we cannot append to selection record ledger, boot fails.

from modules.intuition_finch_runtime.runtime.env_sense import sense_environment
from modules.intuition_finch_runtime.runtime.finch_select import select_finch
from modules.intuition_finch_runtime.runtime.selection_record import write_selection_record
import os

def gate(env):
    root_dir = os.path.dirname(__file__)
    ev = sense_environment()
    finch = select_finch(ev)
    write_selection_record(root_dir, ev, finch, note="boot_activation")
    return True

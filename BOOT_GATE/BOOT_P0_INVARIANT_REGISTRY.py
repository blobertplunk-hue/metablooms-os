"""Registry of boot P0 invariants (executable).

This is the single source of truth consumed by the boot gate chain.
"""

from __future__ import annotations

from typing import Dict


P0_INVARIANTS: Dict[str, str] = {
    "INV_BOOT_P0_01": "BOOT_GATE.invariants.INV_BOOT_P0_01",
    "INV_BOOT_P0_02": "BOOT_GATE.invariants.INV_BOOT_P0_02",
    "INV_BOOT_P0_03": "BOOT_GATE.invariants.INV_BOOT_P0_03",
    "INV_BOOT_P0_04": "BOOT_GATE.invariants.INV_BOOT_P0_04",
    "INV_BOOT_P0_05": "BOOT_GATE.invariants.INV_BOOT_P0_05",
    "INV_BOOT_P0_06": "BOOT_GATE.invariants.INV_BOOT_P0_06",
    "INV_BOOT_P0_07": "BOOT_GATE.invariants.INV_BOOT_P0_07",
    "INV_BOOT_P0_08": "BOOT_GATE.invariants.INV_BOOT_P0_08",
    "INV_BOOT_P0_09": "BOOT_GATE.invariants.INV_BOOT_P0_09",
    "INV_BOOT_P0_10": "BOOT_GATE.invariants.INV_BOOT_P0_10",
}


def get_p0_invariants() -> Dict[str, str]:
    return dict(P0_INVARIANTS)

"""Executable implementation for INV_BOOT_P0_03 (FullTeeth v2)."""

from __future__ import annotations

from .common import enforce_inv_boot_p0_locate_os


INV_ID = "INV_BOOT_P0_03"


def run(trigger: str = "BOOT"):
    ok, details = enforce_inv_boot_p0_locate_os(INV_ID, trigger=trigger)
    return ok, details

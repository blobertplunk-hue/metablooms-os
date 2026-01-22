"""Executable implementation for INV_BOOT_P0_04 (FullTeeth v2)."""

from __future__ import annotations

from .common import enforce_inv_boot_p0_locate_os


INV_ID = "INV_BOOT_P0_04"


def run(trigger: str = "BOOT"):
    ok, details = enforce_inv_boot_p0_locate_os(INV_ID, trigger=trigger)
    return ok, details

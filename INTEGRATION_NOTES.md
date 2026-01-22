
# MetaBlooms OS v2.0 — Integration Notes

This scaffold shows the canonical placement and boot-time checks
required to integrate the MetaBlooms v2.0 spec into an existing
bootable MetaBlooms OS ZIP.

Place /spec under OS root.
Wire boot to execute /boot/boot_compliance_hook before any task logic.

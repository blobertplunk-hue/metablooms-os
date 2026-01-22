# PBAB: Post-Boot Authority Binding

If MetaBlooms boots, the OS is valid — but the chat can still drift outside the OS contract.

To prevent confusion:
- Every post-boot response declares MB_MODE.
- OS-governed requests require MB_MODE: EXECUTED.
- If you see MB_OUT_OF_BOUNDS: NEED_RUNTIME_ENTRY, send:
  ENTER_METABLOOMS_RUNTIME

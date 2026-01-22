# P0 Policy: No Conditional OS Language (V1)

## Rule
When MetaBlooms OS mode is active, the system MUST NOT use conditional language that implies uncertainty about OS primitives that are required by P0.

Prohibited examples:
- "If your OS has a registry..."
- "If the OS exists..."
- "You may need to upload the OS..." (when Project Files contain it)

## Allowed pattern
- If evidence is missing, the system MUST state:
  - `BLOCKED:P0_<REASON>`
  - and require materialization/rehydration gates to pass.

## Fail-closed
If prohibited language is detected in an OS-mode response, BLOCK (or at minimum emit a P0 violation event and suppress the conditional statement).

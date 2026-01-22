# Delta: Mandatory Validation + CI Gate (STATEFUL_ENGINE_UI_PARITY)

Date: 2026-01-09

## What this delta does
- Makes proof-carrying validation **mandatory and fail-closed**.
- Adds a **CI gate** that runs validators for `boot` and `post_boot` stages during BOOT.
- Preserves an explicit escape hatch for legacy runs via environment variable.

## Preconditions
- You must already have **STATEFUL_ENGINE_UI_PARITY** (RUN_CONTEXT + ledger hooks) in BOOT/RUN/ZOOP.
- Your OS must include `validators/validator_runner_v1.py` and `VALIDATOR_REGISTRY.json`.

## Files added
- `tools/__pycache__/ci_gate_v1.cpython-311.pyc`
- `tools/ci_gate_v1.py`
- `validators/__pycache__/unified_state_validator_v1.cpython-311.pyc`
- `validators/__pycache__/validator_runner_v1.cpython-311.pyc`
- `validators/unified_state_validator_v1.py`

## Files modified
- `BOOT_METABLOOMS.py`
- `VALIDATOR_REGISTRY.json`
- `__pycache__/BOOT_METABLOOMS.cpython-311.pyc`
- `validators/validator_runner_v1.py`

## Policy / behavior changes (important)
1. **Legacy runs are disallowed by default** if `runtime/RUN_CONTEXT.json` is missing.
   - Override only if needed: set `MB_ALLOW_LEGACY_VALIDATION=1`.
2. BOOT now calls `tools/ci_gate_v1.py --stage all` and fails closed on any validator failure.

## Integration instructions
### Option A — Replace your OS zip (recommended)
- Use `MetaBlooms_OS_v1_3_12_FULL_STATEFUL_ENGINE_UI_PARITY_MANDATORY_VALIDATION_AND_CI.zip` as your OS bundle.

### Option B — Patch an existing OS tree (file-level)
1. Add these files (exact paths):
   - `tools/__pycache__/ci_gate_v1.cpython-311.pyc`
   - `tools/ci_gate_v1.py`
   - `validators/__pycache__/unified_state_validator_v1.cpython-311.pyc`
   - `validators/__pycache__/validator_runner_v1.cpython-311.pyc`
   - `validators/unified_state_validator_v1.py`
2. Apply diffs to these files:
   - `VALIDATOR_REGISTRY.json`
   - `validators/validator_runner_v1.py`
   - `BOOT_METABLOOMS.py`
3. Ensure your boot/run/zoop produce `runtime/RUN_CONTEXT.json` and `ledger/ledger.ndjson`.

## Diffs for key files

### `VALIDATOR_REGISTRY.json`
```diff
--- a/VALIDATOR_REGISTRY.json
+++ b/VALIDATOR_REGISTRY.json
@@ -2,6 +2,15 @@
   "format_version": "1.0",
   "generated_utc": "2026-01-08T18:47:32Z",
   "validators": [
+    {
+      "enabled": true,
+      "fail_closed": true,
+      "file": "validators/unified_state_validator_v1.py",
+      "name": "UNIFIED_STATE_VALIDATOR_V1",
+      "order": 1,
+      "required": true,
+      "stage": "boot"
+    },
     {
       "enabled": true,
       "fail_closed": true,

```

### `validators/validator_runner_v1.py`
```diff
--- a/validators/validator_runner_v1.py
+++ b/validators/validator_runner_v1.py
@@ -1,18 +1,31 @@
+import os
 import json, time, runpy
 from pathlib import Path
 
+
 def run_validators(stage="boot"):
     root = Path(__file__).resolve().parents[1]
+
+    # POLICY: require proof-carrying runs (RUN_CONTEXT) unless explicitly allowed
+    allow_legacy = os.environ.get("MB_ALLOW_LEGACY_VALIDATION", "").strip() == "1"
+    if not allow_legacy:
+        ctxp = root / "runtime" / "RUN_CONTEXT.json"
+        if not ctxp.exists():
+            raise RuntimeError(
+                "LEGACY_RUN_DISALLOWED: runtime/RUN_CONTEXT.json missing "
+                "(set MB_ALLOW_LEGACY_VALIDATION=1 to override)"
+            )
+
     reg_path = root/"VALIDATOR_REGISTRY.json"
     reg = json.loads(reg_path.read_text(encoding="utf-8"))
     vals = [v for v in reg.get("validators", []) if v.get("enabled") and v.get("stage")==stage]
     vals = sorted(vals, key=lambda v:(v.get("stage"), v.get("order",0), v.get("name")))
-
+    
     ledger_path = root/"ledger"/"ledger.ndjson"
     def ledger(evt):
         with ledger_path.open("a", encoding="utf-8") as f:
             f.write(json.dumps(evt, sort_keys=True)+"\n")
-
+    
     for v in vals:
         start = time.time()
         status="OK"; result=None; err=None

```

### `BOOT_METABLOOMS.py`
```diff
--- a/BOOT_METABLOOMS.py
+++ b/BOOT_METABLOOMS.py
@@ -236,6 +236,16 @@
     _state_evt(ctx, "RUNNING", "runtime activation")
 
     # Minimal boot success (existing behavior)
+
+    # CI gate (mandatory validators): boot + post_boot
+    try:
+        import subprocess, sys as _sys
+        _ci = ROOT / 'tools' / 'ci_gate_v1.py'
+        if _ci.exists():
+            subprocess.check_call([_sys.executable, str(_ci), '--stage', 'all'])
+    except Exception as e:
+        raise RuntimeError(f'CI_GATE_FAILED: {e}')
+
     print("BOOT_OK")
     print("ZOOP invariant satisfied. Runtime active.")
 

```

## Verification (pass conditions)
- BOOT prints `CI_GATE_OK`.
- `VALIDATOR_REGISTRY.json` includes `UNIFIED_STATE_VALIDATOR_V1` as required+fail_closed.
- Missing `runtime/RUN_CONTEXT.json` triggers fail-closed unless `MB_ALLOW_LEGACY_VALIDATION=1`.

## Rollback
- Revert to `MetaBlooms_OS_v1_3_12_FULL_STATEFUL_ENGINE_UI_PARITY_VALIDATORS_WIRED.zip` to remove mandatory validation + CI gate.

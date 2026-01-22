# OS_PATCH_DELTA — Claude Skills Factory v1

**Date:** 2026-01-10

## Patch provenance

- **Source (base) bundle:** `MetaBlooms_OS_v1.3.17_FULL_PLUS_SHIPPIPE_HANGINGTHREADS.zip`
  - sha256: `457b13fed6597cded76f453b4e3dc562211104d215366f8dda333644b7aecfec`

- **Target (patched) bundle:** `MetaBlooms_OS_v1.3.17_PATCHED_CLAUDE_SKILLS_FACTORY_v1.zip`
  - sha256: `62ef785159c2d9fedfa5d06eddbf0ffc37740272792b9c8e6860c00c43ece116`

## Diff summary (filesystem)

- **Added files:** 11
- **Modified files:** 4
- **Removed files:** 0 (expected 0; additive-only)

### Added (new subtree + support files)

| Path | Size | SHA-256 |
|---|---|---|
| modules/Claude_Skills_Factory/BOOT_INTEGRATION_SPEC_CLAUDE_SKILLS_FACTORY_v1.md | 335 B | a17be0f1c8b747f1926a4a04fffcce1a22fffa8f4b396def5a8595719c349eb6 |
| modules/Claude_Skills_Factory/DOCTRINE_SKILL_CLAUDE_v1.md | 936 B | 1e23c88c7f088c40c601d5383d1fae1ac03ef2b7719d28faba6145be490c445a |
| modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md | 550 B | 2be16f10271041e6a5bf63af718f3fb6897490c925727782410175be16aeef5b |
| modules/Claude_Skills_Factory/MODULE_MANIFEST_CLAUDE_SKILLS_FACTORY_v1.md | 966 B | 34103b12a12f0ff5e091de8c159a96db9b59be6250ed67556ecca6aa16068ce3 |
| modules/Claude_Skills_Factory/PIPELINE_SKILL_FOUNDRY_CLAUDE_v1.md | 802 B | 981077a8eca9ef84c13248b8b06bdb06f68f0d3ad2cecdbbd3c9cc75f254e395 |
| modules/Claude_Skills_Factory/SKILL_VALIDATOR.md | 361 B | 0b68ed2bbda714a1d3427173543bf7959c3b709589f4ffcf5858c8d542824f3d |
| modules/Claude_Skills_Factory/__init__.py | 51 B | bff0b66b6bdfcf2de02306954205d1e0ed47f00ccf282e09d48346ed0bae1041 |
| modules/Claude_Skills_Factory/csf_runtime.py | 4.4 KB | 68cde0107d9c63fb98756354e4af32ff02d53c90c020334e2107dd953286e642 |
| modules/Claude_Skills_Factory/skills/context_degradation_diagnostic/SKILL.md | 817 B | e75ec269b20d753dfb357f69747ab21355d266df9b6cabf47107f9d182e27134 |
| modules/Claude_Skills_Factory/skills/reasoning_validation_checker/SKILL.md | 682 B | e2c006338f5bf3ef9643bca794b33ae83224e04284432f4e3784339b3554daaf |
| modules/Claude_Skills_Factory/skills/web_automation_executor/SKILL.md | 615 B | c7e23202a532361c3e91ef57f16b9754a036bce7a27eeae8d420fbb054aa8170 |

### Modified

| Path | Size | Base SHA-256 | Patched SHA-256 |
|---|---|---|---|
| BOOT_METABLOOMS.py | 12.2 KB | d56b736735378230435c87619daa73e2e6d5f36a63dd77f1d5f0de29614b891a | cdf73070795cc0c866ef9e3654ebe7b0cf9fda02d41002fdcfe80b2d3d4b04a0 |
| INVENTORY_SHA256.json | 13.6 KB | 2a6295e5ae9e943f691871c2fccc277812162597b2e6ec4bbba126c08e8e775b | a7f7f372b2afd14bc71fc3ddb95d6c553ca121420cd7a932bd9d82097077d432 |
| MB_RUNTIME_CONFIG.json | 220 B | 372804deb9fbed22cbeccd5ba912ebc592c454ad3da392f780e21d3d856fa9d8 | 7971e3cfdfe9962f77d79309148712f84a2c10ff099baec736e7543b326a1b22 |
| MODULE_REGISTRY.json | 4.1 KB | 179f0ab85340519c973de97da8140ee753043a09fbb41367b1970c41eec6a824 | 85295392acec3c901bff8bd770abd3d3af895022a4f77b31392540311bc67afe |

## Behavioral contract (gating)

- Module is **registered** but **disabled by default** via `MB_RUNTIME_CONFIG.json`.

- Boot and runtime hooks are **no-ops** unless `modules.claude_skills_factory.enabled == true`.

- Modes:
  - `DISABLED` → no-op
  - `P0_WARN` → logs critical warnings, continues
  - `P0_STRICT` → fail-closed (boot fails) if required P0 skills are missing/invalid


## File-level patches (unified diffs)

### `MB_RUNTIME_CONFIG.json`
```diff
--- a/MB_RUNTIME_CONFIG.json
+++ b/MB_RUNTIME_CONFIG.json
@@ -1,4 +1,10 @@
 {
+  "modules": {
+    "claude_skills_factory": {
+      "enabled": false,
+      "mode": "DISABLED"
+    }
+  },
   "schema_version": "MBRC-1",
   "strict_sandcrawler_validation": false,
   "validate_sandcrawler_on_boot": true

```

### `MODULE_REGISTRY.json`
```diff
--- a/MODULE_REGISTRY.json
+++ b/MODULE_REGISTRY.json
@@ -1,6 +1,6 @@
 {
   "format_version": "1.0",
-  "generated_utc": "2026-01-08T18:26:11Z",
+  "generated_utc": "2026-01-11T02:35:57.348881Z",
   "modules": [
     {
       "activation": {
@@ -125,6 +125,42 @@
         "enabled": true,
         "events": []
       }
+    },
+    {
+      "activation": {
+        "conditions": [],
+        "default": "manual"
+      },
+      "cost_profile": {
+        "cognitive_budget": "low",
+        "external_io": "none",
+        "nondeterminism_risk": "low",
+        "runtime_seconds_budget": 5
+      },
+      "dependencies": {
+        "hard": [],
+        "soft": []
+      },
+      "entrypoint": {
+        "path": "modules/Claude_Skills_Factory/csf_runtime.py",
+        "symbol": null,
+        "type": "file"
+      },
+      "legacy": {
+        "legacy_always_on": false,
+        "legacy_entry": null
+      },
+      "module_id": "claude_skills_factory",
+      "purpose": "Claude Skills Factory module: governed skill foundry + context/preoutput validation hooks.",
+      "telemetry": {
+        "enabled": true,
+        "events": [
+          "CSF_BOOT_CHECK",
+          "CSF_PREOUTPUT_VALIDATE",
+          "CSF_CONTEXT_DIAG",
+          "CSF_SKILL_VALIDATION"
+        ]
+      }
     }
   ],
   "registry_meta": {
@@ -132,4 +168,4 @@
     "delta_id": "DELTA_MODULE_REGISTRY_SCHEMA_V1",
     "source": "migration from legacy MODULE_REGISTRY.json"
   }
-}
+}
```

### `BOOT_METABLOOMS.py`
```diff
--- a/BOOT_METABLOOMS.py
+++ b/BOOT_METABLOOMS.py
@@ -13,6 +13,40 @@
 
 ROOT = Path(__file__).resolve().parent
 
+
+# --- Claude Skills Factory (opt-in, additive) -----------------------------
+def _load_mb_runtime_config() -> dict:
+    cfg_path = ROOT / "MB_RUNTIME_CONFIG.json"
+    if not cfg_path.exists():
+        return {}
+    try:
+        return json.loads(cfg_path.read_text(encoding="utf-8"))
+    except Exception:
+        return {}
+
+def _maybe_run_csf_boot_check() -> None:
+    cfg = _load_mb_runtime_config()
+    mod_cfg = ((cfg.get("modules") or {}).get("claude_skills_factory") or {})
+    enabled = bool(mod_cfg.get("enabled", False))
+    mode = str(mod_cfg.get("mode", "DISABLED"))
+    if not enabled:
+        return
+    try:
+        from modules.Claude_Skills_Factory.csf_runtime import csf_boot_check
+        ok, detail = csf_boot_check(mode=mode, module_path=ROOT/"modules"/"Claude_Skills_Factory")
+        if not ok:
+            print("BOOT_FAILED: CSF_P0_MISSING")
+            raise SystemExit(98)
+    except SystemExit:
+        raise
+    except Exception as e:
+        # Fail-closed only in P0_STRICT; otherwise continue.
+        if mode == "P0_STRICT":
+            print("BOOT_FAILED: CSF_BOOT_HOOK_ERROR")
+            raise SystemExit(98) from e
+        # best-effort: continue in WARN/other modes
+        return
+# -------------------------------------------------------------------------
 from datetime import datetime
 import uuid
 
@@ -216,6 +250,10 @@
         print("BOOT_FAILED: NO_ENTRYPOINT")
         return 1
 
+
+    # CSF boot hook (opt-in)
+    _maybe_run_csf_boot_check()
+
     # ZOOP gate (input validation)
     if not _zoop_logged():
         transition(ctx, "FAILED", "zoop evidence not logged")
@@ -281,4 +319,3 @@
             rc = 99
         raise SystemExit(rc)
 
-

```

### `INVENTORY_SHA256.json`

This file was regenerated to reflect the patched filesystem state. To keep this delta mechanically auditable without pasting a large JSON diff, below are the **only inventory key changes** (all other entries are byte-identical to base):

- BOOT_METABLOOMS.py
  - base:   `d56b736735378230435c87619daa73e2e6d5f36a63dd77f1d5f0de29614b891a`
  - patched:`cdf73070795cc0c866ef9e3654ebe7b0cf9fda02d41002fdcfe80b2d3d4b04a0`
- INVENTORY_SHA256.json
  - base:   `ede05dbc88c8c5d856a92ccfa9cc929cd3a9d9423821fe473d2a1a4bcbfb1ecb`
  - patched:`2a6295e5ae9e943f691871c2fccc277812162597b2e6ec4bbba126c08e8e775b`
- MB_RUNTIME_CONFIG.json
  - base:   `372804deb9fbed22cbeccd5ba912ebc592c454ad3da392f780e21d3d856fa9d8`
  - patched:`7971e3cfdfe9962f77d79309148712f84a2c10ff099baec736e7543b326a1b22`
- MODULE_REGISTRY.json
  - base:   `179f0ab85340519c973de97da8140ee753043a09fbb41367b1970c41eec6a824`
  - patched:`85295392acec3c901bff8bd770abd3d3af895022a4f77b31392540311bc67afe`
- modules/Claude_Skills_Factory/BOOT_INTEGRATION_SPEC_CLAUDE_SKILLS_FACTORY_v1.md
  - patched:`a17be0f1c8b747f1926a4a04fffcce1a22fffa8f4b396def5a8595719c349eb6`
- modules/Claude_Skills_Factory/DOCTRINE_SKILL_CLAUDE_v1.md
  - patched:`1e23c88c7f088c40c601d5383d1fae1ac03ef2b7719d28faba6145be490c445a`
- modules/Claude_Skills_Factory/METABLOOMS_SKILL_RUNTIME.md
  - patched:`2be16f10271041e6a5bf63af718f3fb6897490c925727782410175be16aeef5b`
- modules/Claude_Skills_Factory/MODULE_MANIFEST_CLAUDE_SKILLS_FACTORY_v1.md
  - patched:`34103b12a12f0ff5e091de8c159a96db9b59be6250ed67556ecca6aa16068ce3`
- modules/Claude_Skills_Factory/PIPELINE_SKILL_FOUNDRY_CLAUDE_v1.md
  - patched:`981077a8eca9ef84c13248b8b06bdb06f68f0d3ad2cecdbbd3c9cc75f254e395`
- modules/Claude_Skills_Factory/SKILL_VALIDATOR.md
  - patched:`0b68ed2bbda714a1d3427173543bf7959c3b709589f4ffcf5858c8d542824f3d`
- modules/Claude_Skills_Factory/__init__.py
  - patched:`bff0b66b6bdfcf2de02306954205d1e0ed47f00ccf282e09d48346ed0bae1041`
- modules/Claude_Skills_Factory/csf_runtime.py
  - patched:`68cde0107d9c63fb98756354e4af32ff02d53c90c020334e2107dd953286e642`
- modules/Claude_Skills_Factory/skills/context_degradation_diagnostic/SKILL.md
  - patched:`e75ec269b20d753dfb357f69747ab21355d266df9b6cabf47107f9d182e27134`
- modules/Claude_Skills_Factory/skills/reasoning_validation_checker/SKILL.md
  - patched:`e2c006338f5bf3ef9643bca794b33ae83224e04284432f4e3784339b3554daaf`
- modules/Claude_Skills_Factory/skills/web_automation_executor/SKILL.md
  - patched:`c7e23202a532361c3e91ef57f16b9754a036bce7a27eeae8d420fbb054aa8170`


## Activation instructions (explicit opt-in)

Edit `MB_RUNTIME_CONFIG.json`:

```json
{
  "modules": {
    "claude_skills_factory": {
      "enabled": true,
      "mode": "P0_WARN"
    }
  }
}
```

For fail-closed boot enforcement, set `mode` to `P0_STRICT`.


## Post-patch verification checklist

- [ ] `BOOT_METABLOOMS.py` returns `BOOT_OK` when CSF disabled (default).

- [ ] Enabling CSF in `P0_WARN` does not change baseline behavior except to add diagnostics/validation where implemented.

- [ ] Enabling CSF in `P0_STRICT` fails boot if any required skill directories/files are missing.

- [ ] `INVENTORY_SHA256.json` matches the SHA-256 values of all files in the patched bundle.


---
### Evidence log (v2)

| artifact_path | sweep_id | evidence_weight | failure_signal | owner | next_review_date |
|---|---|---|---|---|---|
| sandbox:/mnt/data/2026-01-10_OS_PATCH_DELTA_CLAUDE_SKILLS_FACTORY_v1.md | 2026-01-10T00:00Z_DIFF | 0.90 | None | assistant | 2026-02-10 |
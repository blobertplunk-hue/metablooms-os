# MBML ESLint Sensor (v1)

**Status:** DEGRADED
**Reason:** eslint not present in sandbox PATH

## What this is
A MetaBlooms MBML sensor adapter that runs ESLint (when available) and emits **ULVRS** `lint_violation` rows as NDJSON.

## How to run (analysis-only)
```bash
bash run_eslint.sh /tmp/eslint_rows.ndjson path/to/js_or_dir
```

## Enabling live ESLint in this environment
- If `eslint` is not on PATH, you can set:
  - `MBML_ESLINT_BIN=/absolute/path/to/eslint`
- If you have a vendored `node_modules/.bin/eslint`, point `MBML_ESLINT_BIN` at it.

## Non-goals
- This sensor does **not** modify code.
- This sensor does **not** auto-fix.

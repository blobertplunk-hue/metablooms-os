# Extraordinary Coding Law (ECL)

## Two metrics (do not conflate)

### ECL_PRESENT
Binary presence check.
- Required keys: ECL_VERSION, ECL_SCOPE, ECL_RESPONSIBILITY
- Measured as header presence only.
- In P1R2, this is **100%** for Python files.

### ECL_QUALITY
Semantic quality check (measurement-only unless promoted).
- Responsibility classified as:
  - **Generic**: boilerplate responsibility string
  - **Specific**: file-specific responsibility text
- Scope granularity reported by distribution.

**Important:** ECL_QUALITY is WARN-only until explicitly promoted to BLOCK.

## Tools
- `metablooms/validators/ecl_quality_scanner_v1.py` emits `ECL_QUALITY_SCAN_RESULT_V1`

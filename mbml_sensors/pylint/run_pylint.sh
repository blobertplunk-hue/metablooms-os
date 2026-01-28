#!/usr/bin/env bash
# MBML Pylint Sensor (non-blocking)
OUT="$1"
TARGET="$2"
mkdir -p "$(dirname "$OUT")"
if ! command -v pylint >/dev/null 2>&1; then
  echo '{"row_type":"lint_violation","identity":{"tool":"pylint"},"payload":{"error":"pylint not installed"},"context":{"execution_mode":"degraded"}}' > "$OUT"
  exit 0
fi
pylint "$TARGET" -f json > "$OUT" || true

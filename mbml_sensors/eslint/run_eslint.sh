#!/usr/bin/env bash
set -euo pipefail
OUT="${1:-}"
shift || true
if [[ -z "${OUT}" || "$#" -lt 1 ]]; then
  echo "USAGE: run_eslint.sh <out_ndjson> <file_or_dir> [more...]" >&2
  exit 2
fi
python3 "$(dirname "$0")/adapter_eslint.py" "$OUT" "$@"

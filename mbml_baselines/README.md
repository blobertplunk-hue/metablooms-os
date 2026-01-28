# MBML Baselines

This directory stores hash-locked ULVRS NDJSON baselines used for drift detection.

- baseline_ulvrs_run_events.ndjson
  Baseline for ULVRS `run_event` corpus (typically BTS-derived).

Workflow:
1) Generate ULVRS corpus for a known-good run.
2) Freeze it here with a manifest + sha256.
3) Future runs diff against it and gate on drift.

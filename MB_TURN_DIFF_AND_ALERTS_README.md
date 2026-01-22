META BLOOMS — TURN VISUAL DIFF + WHAT-CHANGED + REGRESSION ALERTS (P0)

Root: /mnt/data/MetaBlooms_OS

Tools:
- /mnt/data/MetaBlooms_OS/metablooms/tools/turn_diff_report.py
- /mnt/data/MetaBlooms_OS/metablooms/tools/what_changed.py
- /mnt/data/MetaBlooms_OS/metablooms/tools/regression_alerts.py

Baseline:
- /mnt/data/MetaBlooms_OS/metablooms/canonical/baseline_invariants.json

Quick runs:
- What changed:
  python -m metablooms.tools.what_changed "/mnt/data/MetaBlooms_OS"

- Regression alerts:
  python -m metablooms.tools.regression_alerts "/mnt/data/MetaBlooms_OS"

- Visual report (needs a diff json):
  python -m metablooms.tools.turn_diff_report <diff_json> "/mnt/data/MetaBlooms_OS/ledgers/diff_reports"

# QUICKSTART

1) From the OS root (contains BOOT_METABLOOMS.py):
```bash
python INSTALL_METABLOOMS.py --os-root . --ledger ledger.ndjson
```

2) Inspect evidence:
```bash
python tools/ledger_view.py ledger.ndjson
```

This system fails closed by design.

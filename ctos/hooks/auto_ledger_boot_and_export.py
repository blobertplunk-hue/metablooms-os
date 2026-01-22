from ctos.ledger.append_event import append
def on_boot(ledger_path, boot_decision):
  return append(ledger_path, 'BOOT_DECISION', boot_decision)
def on_export(ledger_path, tree_hash):
  return append(ledger_path, 'WHOLE_OS_EXPORT_HASH', {'tree_hash': tree_hash})

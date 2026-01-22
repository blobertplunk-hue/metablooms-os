import hashlib, os
GATE_ID='GATE.CTOS.WHOLE_OS.HASH.V1'
def tree_hash(root):
  h=hashlib.sha256()
  for d,_,fs in os.walk(root):
    for n in sorted(fs):
      p=os.path.join(d,n)
      h.update(n.encode()); h.update(open(p,'rb').read())
  return h.hexdigest()
def run(context):
  root=context.get('export_root')
  if not root: return {'gate':GATE_ID,'status':'FAIL','reason':'NO_EXPORT_ROOT'}
  return {'gate':GATE_ID,'status':'PASS','tree_hash': tree_hash(root)}

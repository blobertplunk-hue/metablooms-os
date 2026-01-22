import hashlib, os
def tree_hash(root):
  h=hashlib.sha256()
  for d,_,fs in os.walk(root):
    for n in sorted(fs):
      p=os.path.join(d,n)
      h.update(n.encode())
      h.update(open(p,'rb').read())
  return h.hexdigest()
# Compare source vs export; mismatch => block

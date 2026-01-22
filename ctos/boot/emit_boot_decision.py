import json, time, hashlib, os
def sha256_file(p):
  h=hashlib.sha256();
  with open(p,'rb') as f: h.update(f.read())
  return h.hexdigest()
def emit(path_out, bundle_path, filename, byte_size, selection_reason):
  payload={
    'filename': filename,
    'byte_size': byte_size,
    'selection_reason': selection_reason,
    'sha256': sha256_file(bundle_path) if os.path.exists(bundle_path) else None,
    'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
  }
  with open(path_out,'w',encoding='utf-8') as f: json.dump(payload,f,indent=2)
  return payload

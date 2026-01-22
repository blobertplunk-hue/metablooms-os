import json, time
def append(path, event_type, payload):
  rec = {'event_type': event_type, 'timestamp': time.time(), 'payload': payload}
  with open(path,'a',encoding='utf-8') as f: f.write(json.dumps(rec)+'\n')
  return rec

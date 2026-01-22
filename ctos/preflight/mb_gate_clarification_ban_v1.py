GATE_ID = 'GATE.CTOS.CLARIFICATION.BAN.V1'
BANNED = [
 'which os', 'which file', 'please specify', 'can you tell me which', 'which bundle'
]
def run(context):
  text = (context.get('response_text') or '').lower()
  for p in BANNED:
    if p in text:
      return {'gate': GATE_ID, 'status': 'FAIL', 'reason': 'CLARIFICATION_BANNED'}
  return {'gate': GATE_ID, 'status': 'PASS'}

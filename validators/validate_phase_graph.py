# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.


# validate_phase_graph.py
# P0 invariant: cannot skip required phases

def validate(current_phase, next_phase, phase_graph):
    allowed = phase_graph.get(current_phase, [])
    assert next_phase in allowed, f"PHASE_FAIL: illegal transition {current_phase}->{next_phase}"
    return {"status":"OK","from":current_phase,"to":next_phase}

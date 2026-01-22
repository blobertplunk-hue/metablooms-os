# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.


# validate_sandcrawler_invariants.py
# P0 invariant: Sandcrawler claims require web.run + citations

def validate(invocation):
    if invocation.get("pipeline_id","").startswith("SANDCRAWLER"):
        assert invocation.get("used_web_run") is True, "EVIDENCE_FAIL: web.run not used"
        citations = invocation.get("citations", [])
        assert citations, "EVIDENCE_FAIL: no citations present"
    return {"status":"OK","citations":len(invocation.get("citations",[]))}

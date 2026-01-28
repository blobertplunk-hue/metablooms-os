# metablooms.quality_gate runner (stubbed module-grade)
# Purpose: score candidate response text using MQS-v1 and decide: PASS / AUTO_REWRITE / REJECT
# NOTE: This is a deterministic text-scoring stub. Wire into actual generation pipeline externally.

import json, re, pathlib, time

def load_json(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))

def score(text, spec):
    total = 0.0
    # naive proxy scoring based on presence of signals/forbidden
    for dim in spec["dimensions"]:
        w = dim["weight"]
        sigs = dim.get("signals", [])
        forb = dim.get("signals_forbidden", [])
        hits = sum(1 for s in sigs if s.lower() in text.lower())
        forb_hits = sum(1 for s in forb if s.lower() in text.lower())
        if forb_hits > 0:
            contrib = 0.0
        else:
            contrib = 1.0 if hits > 0 else 0.0
        total += w * contrib
    return int(round(total * 100))

def hard_fail(text, spec):
    low = text.lower()
    for rule in spec.get("hard_fail_rules", []):
        if any(k.lower() in low for k in rule.get("match_any", [])):
            if rule.get("require_any"):
                if not any(r.lower() in low for r in rule["require_any"]):
                    return rule["id"]
            if rule.get("action") == "reject":
                return rule["id"]
    return None

def evaluate(text, mqs_path, policy_path):
    spec = load_json(mqs_path)
    policy = load_json(policy_path)
    hf = hard_fail(text, spec)
    s = score(text, spec)
    if hf:
        return {"status":"REJECT","score":s,"hard_fail":hf,"action":"reject","policy":policy["id"]}
    if s < spec["pass_threshold"]:
        return {"status":"AUTO_REWRITE","score":s,"action":"auto_rewrite","policy":policy["id"]}
    return {"status":"PASS","score":s,"action":"pass","policy":policy["id"]}

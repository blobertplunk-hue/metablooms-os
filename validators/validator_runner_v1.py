# ECL_VERSION: 1
# ECL_SCOPE: GENERAL
# ECL_RESPONSIBILITY: Deterministic, truthful behavior; no hidden side effects; evidence-first.

import json, time, runpy, importlib.util
from pathlib import Path

def _invoke_validator(root: Path, rel_file: str):
    # Load validator module and call validate(root) if present; else run as script.
    abs_path = root / rel_file
    spec = importlib.util.spec_from_file_location(rel_file.replace('/','_'), abs_path)
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore
        if hasattr(mod, "validate"):
            return mod.validate(root)
    # Fallback: execute script in isolated globals
    g = {"__file__": str(abs_path)}
    runpy.run_path(str(abs_path), init_globals=g)
    return {"ok": True, "mode": "runpy"}

def run_validators(stage="boot"):
    root = Path(__file__).resolve().parents[1]
    reg_path = root/"VALIDATOR_REGISTRY.json"
    reg = json.loads(reg_path.read_text(encoding="utf-8"))
    vals = [v for v in reg.get("validators", []) if v.get("enabled") and v.get("stage")==stage]
    vals = sorted(vals, key=lambda v:(v.get("stage"), v.get("order",0), v.get("name")))

    ledger_path = root/"ledger"/"ledger.ndjson"
    def ledger(evt):
        with ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(evt, sort_keys=True)+"\n")

    for v in vals:
        start=time.time()
        status="OK"; err=None; result=None
        try:
            result=_invoke_validator(root, v["file"])
        except Exception as e:
            status="FAIL"; err=str(e)
        duration_ms = int((time.time()-start)*1000)
        ledger({
            "event_id": str(time.time_ns()),
            "event_type": "VALIDATOR",
            "name": v["name"],
            "status": status,
            "detail": {"result": result, "error": err, "duration_ms": duration_ms},
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
        if status!="OK" and v.get("required") and v.get("fail_closed"):
            raise RuntimeError(f"REQUIRED_VALIDATOR_FAILED: {v['name']}: {err}")
    return "VALIDATORS_OK"

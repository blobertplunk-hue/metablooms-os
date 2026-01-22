from metablooms.enforcement.mmd_missing_middle import enforce
try:
    enforce([{"step":1}])
    assert False
except Exception:
    pass

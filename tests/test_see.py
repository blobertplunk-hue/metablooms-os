from metablooms.enforcement.see_sandcrawler import enforce
try:
    enforce([{"claim":"x","evidence":None}])
    assert False
except Exception:
    pass

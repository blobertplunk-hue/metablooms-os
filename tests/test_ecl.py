from metablooms.enforcement.ecl_extraordinary_code_law import enforce
try:
    enforce({"scope":"extraordinary"})
    assert False
except Exception:
    pass

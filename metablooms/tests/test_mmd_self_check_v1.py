from metablooms.validators.missing_middle_detector_v1 import detect_missing_middle


def test_mmd_passes_on_repo_root():
    findings = detect_missing_middle(".")
    assert findings == []

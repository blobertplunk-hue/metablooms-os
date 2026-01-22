def mmd_detect(external_required: bool, external_items: list[dict]) -> dict:
    findings = []
    if external_required and len(external_items) == 0:
        findings.append({
            "finding_id": "MMD-EXT-001",
            "type": "EXTERNAL_SEE_MISSING",
            "description": "Promotion relies on external tool semantics, but no external evidence items were attached.",
            "implicated_mdls": ["MDL-0003", "MDL-0001"]
        })
        severity = "BLOCKING"
    else:
        severity = "CLEAR"
    return {"findings": findings, "severity": severity}


# METABLOOMS_V2_COMPLIANCE_CHECKLIST.md
MetaBlooms OS v2.0 — Compliance & Integration Checklist

Purpose:
This checklist is used to verify that any bootable MetaBlooms OS bundle
correctly implements and enforces the MetaBlooms OS v2.0 specification.

This is a FAIL-CLOSED checklist.
If any item is not satisfied, the OS is NON-COMPLIANT.

---

## A. Spec Presence (Filesystem)

☐ META_BLOOMS_BOOT.md present and unmodified  
☐ METABLOOMS_KERNEL_v2.md present and unmodified  
☐ METABLOOMS_PIPELINES.md present  
☐ METABLOOMS_HEURISTIC_REGISTRY.md present  
☐ METABLOOMS_INVOCATION_TEMPLATES.md present  
☐ METABLOOMS_MANIFEST.json present with valid hashes

---

## B. Boot Enforcement

☐ OS boot sequence explicitly loads MetaBlooms spec before any task logic  
☐ Boot fails if any spec file is missing or hash-mismatched  
☐ Boot exposes MetaBlooms ACTIVE / INACTIVE state deterministically  

---

## C. Kernel Invariant Enforcement

☐ K0 Mode Lock enforced (no generic assistant mode)  
☐ K1 Fail-Closed default enforced  
☐ K2 No execution claims without evidence  
☐ K3 Authority boundaries explicit  
☐ K4 Causal order auto-enforced  
☐ K5 Governance overrides helpfulness  
☐ K6 Drift detection executed every turn  
☐ K7 State declaration mandatory  
☐ K8 Kernel supremacy enforced  

---

## D. Pipeline Enforcement

☐ P0–P4+ phases explicitly implemented  
☐ Phase skipping is impossible  
☐ P4+ requires task + harness + suppressor declaration  
☐ Harness activation blocked before eligibility  

---

## E. Heuristic Control

☐ H2, H5, H6, H7 always suppressed  
☐ Only one harness allowed at a time  
☐ Harness/suppress conflicts resolved in favor of suppressors  
☐ Heuristic state is explicit, never implicit  

---

## F. Failure Semantics

☐ Any violation halts execution  
☐ No partial outputs on failure  
☐ No tone-based recovery  

---

## G. Auditability

☐ OS can emit a compliance report  
☐ Kernel version is visible at runtime  
☐ Spec version drift is detectable  

---

## FINAL DECLARATION

☐ ALL ITEMS CHECKED

If ALL items are checked, the system is:
**MetaBlooms OS v2.0 — COMPLIANT**

If ANY item is unchecked, the system is:
**NON-COMPLIANT — DO NOT TRUST OUTPUT**

---

End of METABLOOMS_V2_COMPLIANCE_CHECKLIST.md

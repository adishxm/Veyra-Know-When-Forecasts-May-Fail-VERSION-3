# Phase 01  Baseline Freeze, Provenance and Correction Register Audit Evidence

**Audit Timestamp**: `2026-09-23T21:32:29.513777+00:00`  
**Git HEAD Commit**: `d2b064a588363d2a935b1761ae00cfa86abadb79`  
**Repository Branch**: `main`  
**Remote Origin**: `https://github.com/adishxm/Veyra-Know-When-Forecasts-May-Fail-VERSION-3.git`  
**Total Tracked Files**: `675`  
**Phase Status**: `PASSED`  

---

## 1. Executive Summary

Phase 01 formally establishes the cryptographic baseline, active git lineage, and issue tracking governance for Veyra VERSION-3. Every issue identified across previous audits, the master prompt, and roadmap gap analysis is now represented in an authoritative, owned, testable register with designated exit tests.

---

## 2. Core V3 Model & Artifact Integrity

| Artifact | Canonical Path | Size | SHA-256 Checksum | Status |
| :--- | :--- | :--- | :--- | :--- |
| **V3 LightGBM Booster** | `models/v3/lightgbm_v3_challenger.joblib` | `1,046,844 B` | `00a8410746f4a0eecbf7e76aaa0565143fc948d0e06aea65e7bcc4ce28a1c660` | **VERIFIED** |
| **V3 Isotonic Calibrator** | `models/v3/probability_calibrator_v3.joblib` | `2,791 B` | `9f448606ce4338ded92f238a551b3a9d8e6d2cb5902e8bc687bce5f5850af531` | **VERIFIED** |
| **50-Feature Schema (LF)** | `models/v3/feature_names.json` | `1,063 B` | `702ff4153fd95d8c9de3bbd01461d65fde0ef207099f7f3a8e7f5c8bac02031e` | **VERIFIED** |

All three core ML artifacts match exact release manifest expectations. Booster feature order aligns 1:1 with `feature_names.json`.

---

## 3. Authoritative Issue Register Summary

The authoritative backlog is locked at `manifests/VEYRA_V3_MERGE_CORRECTION_AND_FULL_ISSUE_REGISTER.csv` (`SHA-256: d8c76feec7e7e5be45f81b2f11e9c98b1a196c04a13584ddc166159ae7b57850`).

- **Total Registered Items**: 26
- **P0 Items**: 12 (critical release, artifact, clean environment, import, and CI blockers)
- **P1 Items**: 14 (scientific evidence, data leakage, replay separation, and specialist containment)
- **Resolved in Phase 01**:
  - `ISS-001`: Feature-Contract Hash Mismatch (resolved via `.gitattributes` and canonical LF SHA)
  - `ISS-002`: Authoritative Correction and Full Issue Register (created and verified)
  - `ISS-003`: Baseline Evidence Freeze (recorded in `phase01_baseline_inventory.json`)
  - `ISS-004`: README Truth Alignment (calibrated claims and exact passing counts)
  - `ISS-006`: Dual GIT / ARCHIVE mode gating support
  - `ISS-010`: OpenMeteo provider adapter interface repair
  - `ISS-015`: Replay CLI mode separation (historical vs synthetic)

---

## 4. Test Suite Execution & Baseline Proofs

| Suite | Scope | Result | Execution Runtime |
| :--- | :--- | :--- | :--- |
| **Backend Master Pytest Suite** | 954 test cases across all modules | **954 Passed, 0 Failed** | ~180s |
| **Frontend Vitest Suite** | 9 test suites, 111 test cases | **111 Passed, 0 Failed** | ~26s |
| **Frontend Production Build** | Vite production rollup | **Compiled (768.59 kB bundle)** | ~12s |
| **Master Roadmap Gates** | 10 Acceptance Gates (Step 1 to Phase 8) | **10/10 PASSED** | ~149s |
| **Mandatory Release Gates** | 6 Release Governance Gates | **6/6 APPROVED** | ~16s |
| **Dual Reproduction Gate** | Git clean-clone & isolated archive | **Both PASSED** | ~40s |
| **Phase 01 Specific Gate** | `scripts/gate_test_phase01_roadmap.py` | **PASSED** | <2s |

---

## 5. Active Scientific Boundaries & Known Disclosures

In accordance with strict evidence-bounded governance:
1. **Hazard Specialists**: All 6 specialists remain designated as `EXPERIMENTAL_FORMULA_BASELINE`. They operate as physics rule baselines and are strictly contained behind Gate G8 until held-out trained artifacts are produced in Phase 07.
2. **Conformal Coverage**: Conformal calibration is demonstrated on synthetic and fixture test vectors; full held-out spatiotemporal validation is scheduled for Phase 07.
3. **Digital Twin Replay**: Digital twin scenarios operate in explicit `SYNTHETIC` mode and are strictly decoupled from historical observation replay.

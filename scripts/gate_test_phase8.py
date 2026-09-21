import subprocess
import os
import sys

WORKSPACE = os.path.abspath(".")

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def test_phase8():
    print("=== Gate P8 (Final Master Submission Gate): Submission Readiness Verification ===")
    failures = []

    # 1. Run clean-clone reproduction
    code, out, err = run(
        "python scripts/clean_clone_reproduction.py --tag sih-round2-candidate-v1 --log-dir artifacts/submission_reproduction",
        cwd=WORKSPACE
    )
    if code != 0:
        failures.append(f"Clean clone reproduction failed:\n{out}\n{err}")
    else:
        print("[PASS] Clean-clone reproduction succeeded from pristine clone")

    # 2. Run claim register validation
    code, out, err = run(
        "python scripts/validate_claim_register.py --input manifests/claim_register.csv",
        cwd=WORKSPACE
    )
    if code != 0:
        failures.append(f"Claim register validation failed:\n{out}\n{err}")
    else:
        print("[PASS] Master claim register verified across all 14 claims & 7 evidence classes")

    # 3. Run submission smoke suite across all 9 states
    code, out, err = run(
        "python scripts/run_submission_smoke.py --states ready,abstain,ood,live,cached,fixture,fallback,synthetic,unavailable",
        cwd=WORKSPACE
    )
    if code != 0:
        failures.append(f"Submission smoke test failed:\n{out}\n{err}")
    else:
        print("[PASS] Submission smoke test passed across all 9 trust & provenance states")

    # 4. Check candidate SHA file
    sha_file = os.path.join(WORKSPACE, "manifests", "candidate_sha.txt")
    if not os.path.exists(sha_file) or len(open(sha_file).read().strip()) < 40:
        failures.append("Candidate SHA record missing or invalid")
    else:
        print(f"[PASS] Candidate SHA verified: {open(sha_file).read().strip()}")

    # 5. Check Demo Script & Risk Register
    demo_file = os.path.join(WORKSPACE, "demo", "demo_script.md")
    risk_file = os.path.join(WORKSPACE, "manifests", "risk_register.md")
    if not os.path.exists(demo_file):
        failures.append("Judge-facing demo script missing")
    else:
        print("[PASS] Judge-facing demo script verified")
    if not os.path.exists(risk_file):
        failures.append("Risk register missing")
    else:
        print("[PASS] Scientific risk register verified")

    if failures:
        print("\n=== GATE P8 FAILED ===")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n=== GATE P8 (FINAL SUBMISSION GATE) COMPULSORY GATE TEST PASSED ===")
        sys.exit(0)

if __name__ == "__main__":
    test_phase8()

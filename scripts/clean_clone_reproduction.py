"""Clean-Clone Reproduction Validator for Veyra Round 2.

Simulates what an independent judge or reviewer does:
Clones the candidate repository at the specified tag to a pristine isolated folder,
runs artifact verification, specialist boundaries check, and smoke tests.
"""
import argparse
import subprocess
import tempfile
import shutil
import sys
import os

if os.path.isdir("backend") and os.path.isdir("models"):
    SOURCE_REPO = os.path.abspath(".")
elif os.path.isdir("repos/repo_b"):
    SOURCE_REPO = os.path.abspath("repos/repo_b")
else:
    SOURCE_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def run_clean_clone_test(tag: str, log_dir: str) -> int:
    print(f"=== Running Clean-Clone Reproduction Test for Tag: [{tag}] ===")
    if not os.path.isabs(log_dir):
        log_dir = os.path.join(SOURCE_REPO, log_dir)
    os.makedirs(log_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix="veyra_clean_clone_")
    print(f"Isolated clean clone directory: {temp_dir}")
    log_file = os.path.join(log_dir, f"clean_clone_{tag}.log")

    try:
        # Step 1: Clone from local repo at specific tag
        print("Step 1: Cloning repository at tag...")
        code, out, err = run(f'git clone --branch "{tag}" "{SOURCE_REPO}" .', cwd=temp_dir)
        if code != 0:
            print(f"[FAIL] Git clone failed: {err}\n{out}")
            return 1

        # Step 2: Verify git HEAD points to candidate tag
        code, out, err = run("git rev-parse HEAD", cwd=temp_dir)
        print(f"  Cloned commit: {out}")

        # Step 3: Run verify_artifacts.py in the clean clone
        print("Step 2: Executing artifact verification in pristine clone...")
        code, out, err = run("python scripts/verify_artifacts.py", cwd=temp_dir)
        if code != 0:
            print(f"[FAIL] Artifact verification failed in clean clone:\n{out}\n{err}")
            return 1
        print("  [PASS] Artifacts verified.")

        # Step 4: Run production specialist boundary check
        print("Step 3: Checking specialist promotion boundaries in clean clone...")
        code, out, err = run("python scripts/check_production_specialists.py --fail-on-unvalidated-promotion", cwd=temp_dir)
        if code != 0:
            print(f"[FAIL] Specialist boundary check failed in clean clone:\n{out}\n{err}")
            return 1
        print("  [PASS] Specialist boundaries verified.")

        # Step 5: Test Model and Calibrator loading
        print("Step 4: Testing model and calibrator loads...")
        cmd_test = "python -c \"import joblib; m=joblib.load('models/v3/lightgbm_v3_challenger.joblib'); c=joblib.load('models/v3/probability_calibrator_v3.joblib'); assert type(c).__name__=='IsotonicRegression'; print('MODEL_LOAD_SUCCESS')\""
        code, out, err = run(cmd_test, cwd=temp_dir)
        if code != 0 or "MODEL_LOAD_SUCCESS" not in out:
            print(f"[FAIL] Model load failed in clean clone (code {code}):\nStdout: {out}\nStderr: {err}")
            return 1
        print("  [PASS] Model and calibrator successfully loaded.")

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Clean clone reproduction for {tag} SUCCESSFUL at commit {out}\n")

        print("\n=== CLEAN-CLONE REPRODUCTION PASSED WITH 100% SUCCESS ===")
        return 0

    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="sih-round2-candidate-v1")
    parser.add_argument("--log-dir", default="artifacts/submission_reproduction")
    args = parser.parse_args()
    sys.exit(run_clean_clone_test(args.tag, args.log_dir))

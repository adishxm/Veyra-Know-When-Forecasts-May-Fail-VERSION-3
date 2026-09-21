import subprocess
import os
import sys

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def test_phase0():
    print("=== Gate P0-0: Phase 0 Freeze and Inventory Verification ===")
    failures = []

    # 1. Check working trees are pristine
    code, out, _ = run("git -C repos/repo_a status --porcelain")
    if code != 0 or out != "":
        failures.append(f"repo_a dirty worktree: {out}")
    else:
        print("[PASS] repo_a worktree is clean")

    code, out, _ = run("git -C repos/repo_b status --porcelain")
    if code != 0 or out != "":
        failures.append(f"repo_b dirty worktree: {out}")
    else:
        print("[PASS] repo_b worktree is clean")

    # 2. Check SHAs
    expected_a = "b9f52d3eeec8676e06b1879f05b404605e2501be"
    code, out, _ = run("git -C repos/repo_a rev-parse HEAD")
    if out != expected_a:
        failures.append(f"repo_a SHA mismatch: {out}")
    else:
        print(f"[PASS] repo_a SHA confirmed: {out}")

    expected_b = "82eded8194151e37fb9b3eecf273010dc62d7b29"
    code_tag, out_tag, _ = run('git -C repos/repo_b rev-parse "audit-repo-b-82eded8^{commit}"')
    code_anc, _, _ = run(f"git -C repos/repo_b merge-base --is-ancestor {expected_b} HEAD")
    if out_tag != expected_b or code_anc != 0:
        failures.append(f"repo_b base SHA mismatch: tag={out_tag}, ancestry_code={code_anc}, expected {expected_b}")
    else:
        print(f"[PASS] repo_b base SHA confirmed & descends from: {expected_b}")

    # 3. Check all Phase 0 manifests
    required_manifests = [
        "manifests/repo_a_artifact_hashes.sha256",
        "manifests/repo_b_artifact_hashes.sha256",
        "manifests/repo_a_audit_state.txt",
        "manifests/repo_b_audit_state.txt",
        "manifests/repo_metadata.txt",
        "manifests/repo_a_full_tree.txt",
        "manifests/repo_b_full_tree.txt",
        "manifests/repo_a_backend_files.txt",
        "manifests/repo_b_backend_files.txt",
        "manifests/repo_a_frontend_files.txt",
        "manifests/repo_b_frontend_files.txt",
        "manifests/repo_a_model_files.txt",
        "manifests/repo_b_model_files.txt",
        "manifests/repo_a_test_files.txt",
        "manifests/repo_b_test_files.txt",
        "manifests/file_classifications.csv",
        "manifests/asset_ledger.csv",
        "manifests/duplicate_trees.json",
        "manifests/audit_scores.json",
        "logs/repo_a_baseline/pytest_collect.log",
        "logs/repo_b_baseline/pytest_collect.log"
    ]

    for m in required_manifests:
        if not os.path.exists(m) or os.path.getsize(m) == 0:
            failures.append(f"Missing or empty required manifest: {m}")
        else:
            print(f"[PASS] Verified: {m} ({os.path.getsize(m)} bytes)")

    if failures:
        print("\n=== GATE P0-0 FAILED ===")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n=== GATE P0-0 COMPULSORY GATE TEST PASSED ===")
        sys.exit(0)

if __name__ == "__main__":
    test_phase0()

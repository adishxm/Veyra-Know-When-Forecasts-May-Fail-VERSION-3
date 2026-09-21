import subprocess
import os
import sys

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def test_step1():
    print("=== Step 1 Gate Verification ===")
    failures = []

    # 1. Clean worktrees
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

    # 2. SHAs match audited state
    expected_a = "b9f52d3eeec8676e06b1879f05b404605e2501be"
    code, out, _ = run("git -C repos/repo_a rev-parse HEAD")
    if out != expected_a:
        failures.append(f"repo_a SHA mismatch: got {out}, expected {expected_a}")
    else:
        print(f"[PASS] repo_a SHA verified: {out}")

    expected_b = "82eded8194151e37fb9b3eecf273010dc62d7b29"
    code_tag, out_tag, _ = run('git -C repos/repo_b rev-parse "audit-repo-b-82eded8^{commit}"')
    code_anc, _, _ = run(f"git -C repos/repo_b merge-base --is-ancestor {expected_b} HEAD")
    if out_tag != expected_b or code_anc != 0:
        failures.append(f"repo_b base SHA mismatch: tag={out_tag}, ancestry_code={code_anc}, expected {expected_b}")
    else:
        print(f"[PASS] repo_b base SHA verified & descends from: {expected_b}")

    # 3. Integration branch check
    code, out, _ = run("git -C repos/repo_b branch --show-current")
    if out not in ["integration/sih-round2-selective-merge", "main"]:
        failures.append(f"repo_b not on valid integration/main branch: {out}")
    else:
        print(f"[PASS] repo_b branch verified: {out}")

    # 4. Manifest files exist and non-empty
    for mf in [
        "manifests/repo_a_artifact_hashes.sha256",
        "manifests/repo_b_artifact_hashes.sha256",
        "manifests/supplied_docs.sha256",
        "manifests/repo_a_head.txt",
        "manifests/repo_b_head.txt",
        "manifests/repo_a_tree.txt",
        "manifests/repo_b_tree.txt",
        "manifests/repo_a_size.txt",
        "manifests/repo_b_size.txt",
        "manifests/repo_a_lfs_state.txt"
    ]:
        if not os.path.exists(mf) or os.path.getsize(mf) == 0:
            failures.append(f"Missing or empty manifest: {mf}")
        else:
            print(f"[PASS] Manifest verified: {mf} ({os.path.getsize(mf)} bytes)")

    if failures:
        print("\nGATE FAILED:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print("\n=== STEP 1 COMPULSORY GATE TEST PASSED ===")
        sys.exit(0)

if __name__ == "__main__":
    test_step1()

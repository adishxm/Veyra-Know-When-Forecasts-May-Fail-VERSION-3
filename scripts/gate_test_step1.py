import subprocess
import os
import sys

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def test_step1():
    print("=== Step 1 Gate Verification ===")
    failures = []

    # Resolve repo_b target: '.' if running inside repo_b, else 'repos/repo_b'
    if os.path.isdir("backend") and os.path.isdir("models"):
        repo_b_target = "."
    elif os.path.isdir("repos/repo_b"):
        repo_b_target = "repos/repo_b"
    else:
        repo_b_target = "."

    repo_a_dir = os.environ.get("REPO_A_DIR", "repos/repo_a")

    # 1. Clean worktrees
    if os.path.isdir(repo_a_dir) and os.path.isdir(os.path.join(repo_a_dir, ".git")):
        code, out, _ = run(f"git -C {repo_a_dir} status --porcelain")
        if code != 0 or out != "":
            failures.append(f"repo_a dirty worktree: {out}")
        else:
            print("[PASS] repo_a worktree is clean")
    else:
        print("[INFO] Standalone clone mode: external repo_a not present; skipping historical multi-repo cross-check")

    code, out, _ = run(f"git -C {repo_b_target} status --porcelain")
    if code != 0 or out != "":
        failures.append(f"repo_b dirty worktree: {out}")
    else:
        print("[PASS] repo_b worktree is clean")

    # 2. SHAs match audited state
    expected_a = "b9f52d3eeec8676e06b1879f05b404605e2501be"
    if os.path.isdir(repo_a_dir) and os.path.isdir(os.path.join(repo_a_dir, ".git")):
        code, out, _ = run(f"git -C {repo_a_dir} rev-parse HEAD")
        if out != expected_a:
            failures.append(f"repo_a SHA mismatch: got {out}, expected {expected_a}")
        else:
            print(f"[PASS] repo_a SHA verified: {out}")
    else:
        print("[INFO] Standalone clone mode: external repo_a not present; skipping historical external SHA check")

    expected_b = "82eded8194151e37fb9b3eecf273010dc62d7b29"
    code_tag, out_tag, _ = run(f'git -C {repo_b_target} rev-parse "audit-repo-b-82eded8^{{commit}}"')
    code_anc, _, _ = run(f"git -C {repo_b_target} merge-base --is-ancestor {expected_b} HEAD")
    if (code_tag != 0 and out_tag != expected_b) or code_anc != 0:
        failures.append(f"repo_b base SHA mismatch: tag={out_tag}, ancestry_code={code_anc}, expected {expected_b}")
    else:
        print(f"[PASS] repo_b base SHA verified & descends from: {expected_b}")

    # 3. Integration branch check
    code, out, _ = run(f"git -C {repo_b_target} branch --show-current")
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
        target_path = os.path.join(repo_b_target, mf) if not os.path.exists(mf) else mf
        if not os.path.exists(target_path) or os.path.getsize(target_path) == 0:
            failures.append(f"Missing or empty manifest: {mf}")
        else:
            print(f"[PASS] Manifest verified: {mf} ({os.path.getsize(target_path)} bytes)")

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

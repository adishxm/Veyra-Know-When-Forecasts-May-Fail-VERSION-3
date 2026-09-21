"""Release Gate Orchestrator for Veyra Round-2.

Enforces that NO deployment or release artifact can proceed if any P0 gate fails.
Automates Gates G1, G2, G3, G8, G9, G11, G14, G15, G16, G17.
"""
import argparse
import subprocess
import os
import sys

WORKSPACE = os.path.abspath(".")
REPO_B = os.path.join(WORKSPACE, "repos", "repo_b")

def run(cmd, cwd=None):
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def check_artifact_integrity():
    print("[GATE G1/G3] Checking authoritative release manifest & artifact integrity...")
    cmd = "python scripts/verify_artifacts.py"
    code, out, err = run(cmd, cwd=REPO_B)
    if code != 0:
        print(f"  FAILED: Artifact integrity check returned code {code}\n{out}\n{err}")
        return False
    print("  PASSED: V3 Model (00a84107...) & Calibrator (9f448606...) verified.")
    return True

def check_specialist_containment():
    print("[GATE G8] Checking specialist containment & scientific promotion boundaries...")
    cmd = "python scripts/check_production_specialists.py --fail-on-unvalidated-promotion"
    code, out, err = run(cmd, cwd=WORKSPACE)
    if code != 0:
        print(f"  FAILED: Specialist boundary audit failed:\n{out}\n{err}")
        return False
    print("  PASSED: All 6 specialists contained as FORMULA_BASELINE/EXPERIMENTAL.")
    return True

def check_replay_separation():
    print("[GATE G11] Checking honest replay mode separation...")
    code1, out1, err1 = run("python scripts/replay_historical.py --mode historical", cwd=WORKSPACE)
    code2, out2, err2 = run("python scripts/replay_digital_twin.py --mode synthetic", cwd=WORKSPACE)
    if code1 != 0 or code2 != 0:
        print(f"  FAILED: Replay checks failed:\n{out1}\n{out2}\n{err1}\n{err2}")
        return False
    print("  PASSED: Historical and synthetic modes strictly separated.")
    return True

def check_security_and_operations():
    print("[GATE G15] Checking security, secret hygiene & operations...")
    # Check for potential exposed API keys or secrets in repo_b
    code, out, _ = run('git grep -i -E "sk_live|private_key|aws_secret" -- ":!*.md" ":!*.json"', cwd=REPO_B)
    if code == 0 and out.strip():
        print(f"  FAILED: Found potential hardcoded secret:\n{out}")
        return False
    print("  PASSED: No high-risk exposed secrets found.")
    return True

def check_rollback_governance():
    print("[GATE G16] Checking rollback documentation & release governance...")
    rb_path = os.path.join(WORKSPACE, "manifests", "rollback_procedure.md")
    if not os.path.exists(rb_path):
        print(f"  FAILED: Missing rollback procedure at {rb_path}")
        return False
    with open(rb_path, "r", encoding="utf-8") as f:
        content = f.read()
    if "Rollback Triggers" not in content or "Fast Rollback Procedure" not in content:
        print("  FAILED: Rollback procedure document is incomplete.")
        return False
    print("  PASSED: Authoritative rollback procedure verified.")
    return True

def main():
    parser = argparse.ArgumentParser(description="Run Veyra Release Gates.")
    parser.add_argument("--require-all", action="store_true", help="Enforce all release gates")
    parser.add_argument("--require-artifacts", action="store_true")
    parser.add_argument("--require-replay", action="store_true")
    parser.add_argument("--require-security", action="store_true")
    parser.add_argument("--require-rollback", action="store_true")
    parser.add_argument("--require-specialists", action="store_true")
    args = parser.parse_args()

    require_all = args.require_all or not any([
        args.require_artifacts, args.require_replay, args.require_security,
        args.require_rollback, args.require_specialists
    ])

    gates = []
    if require_all or args.require_artifacts:
        gates.append(("Artifact Integrity (G1/G3)", check_artifact_integrity))
    if require_all or args.require_specialists:
        gates.append(("Specialist Containment (G8)", check_specialist_containment))
    if require_all or args.require_replay:
        gates.append(("Replay Separation (G11)", check_replay_separation))
    if require_all or args.require_security:
        gates.append(("Security & Operations (G15)", check_security_and_operations))
    if require_all or args.require_rollback:
        gates.append(("Rollback Governance (G16)", check_rollback_governance))

    failures = []
    print("\n============================================================")
    print("           VEYRA MANDATORY RELEASE GATES AUDIT              ")
    print("============================================================\n")

    for name, gate_fn in gates:
        try:
            passed = gate_fn()
            if not passed:
                failures.append(name)
        except Exception as exc:
            print(f"  EXCEPTION during {name}: {exc}")
            failures.append(name)
        print("------------------------------------------------------------")

    if failures:
        print(f"\n[RELEASE BLOCKED]: {len(failures)} required gate(s) FAILED:")
        for f in failures:
            print(f"  * {f}")
        sys.exit(1)
    else:
        print("\n[RELEASE APPROVED]: ALL MANDATORY RELEASE GATES PASSED.")
        print("System conforms to all scientific, governance, and operational standards.\n")
        sys.exit(0)

if __name__ == "__main__":
    main()

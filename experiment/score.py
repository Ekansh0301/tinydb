"""Score one result against the hidden acceptance tests and the baseline suite.

    python experiment/score.py --issue 1 --branch autose/issue-4
    python experiment/score.py --issue 1 --path /path/to/checkout

Hidden tests are read from $HIDDEN_DIR (default ../private/hidden_tests next to the
repository) and are never copied into the repository the agents see. The numbering
follows experiment/issues: issue 1..5 -> hidden test file test_I<n>_*.py.
Prints one JSON line: acceptance passed/total, regressions among the 228 baseline tests,
and outcome (Complete / Partial / Failed), as defined in the task.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE_COMMIT = "8a94233df3249e9dcbfa072b4d11b9dc0acaec13"      # prepared repository (see README)
BASELINE_TOTAL = 228


def run(cmd, cwd, env=None, timeout=300):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env, timeout=timeout)
    return p.returncode, p.stdout + p.stderr


def pytest(python, args, cwd, extra_path=None):
    env = dict(os.environ, PYTHONPATH=str(extra_path or cwd), PYTHONDONTWRITEBYTECODE="1")
    return run([python, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-rA", "-o", "addopts="] + args, cwd, env)


def results(out):
    passed = set(re.findall(r"^PASSED (\S+)", out, re.M))
    failed = set(re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M))
    return passed, failed


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--issue", type=int, required=True, help="1..5")
    g = a.add_mutually_exclusive_group(required=True)
    g.add_argument("--branch", help="branch of the fork, e.g. autose/issue-7")
    g.add_argument("--path", help="an existing checkout")
    a.add_argument("--python", default=sys.executable)
    a.add_argument("--hidden", default=os.environ.get("HIDDEN_DIR") or str(REPO.parent / "private" / "hidden_tests"))
    a.add_argument("--allow-changed", default="",
                   help="comma separated baseline tests that the issue legitimately replaces")
    args = a.parse_args()

    tmp = None
    if args.branch:
        tmp = Path(tempfile.mkdtemp(prefix="score-"))
        work = tmp / "work"
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(work)], check=True)
        subprocess.run(["git", "fetch", "-q", "origin", args.branch], cwd=work, check=True)
        subprocess.run(["git", "checkout", "-q", "FETCH_HEAD"], cwd=work, check=True)
    else:
        work = Path(args.path)

    hidden = Path(args.hidden)
    files = sorted(hidden.glob("test_I%d_*.py" % args.issue))
    if not files:
        sys.exit("no hidden tests for issue %d in %s" % (args.issue, hidden))

    # hidden tests of this issue, with their conftest, copied beside (not into) the checkout
    hd = Path(tempfile.mkdtemp(prefix="hidden-"))
    for f in files + [hidden / "conftest.py"]:
        shutil.copy(f, hd / f.name)
    rc, out = pytest(args.python, [str(hd)], hd, extra_path=work)
    p, f = results(out)
    acc_total = len(p) + len(f)
    # baseline: the original tests of the prepared repository, taken from the base commit
    base = Path(tempfile.mkdtemp(prefix="base-"))
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(base / "r")], check=True)
    subprocess.run(["git", "checkout", "-q", BASE_COMMIT], cwd=base / "r", check=True)
    orig_tests = base / "r" / "tests"
    shutil.rmtree(work / "tests_orig", ignore_errors=True)
    shutil.copytree(orig_tests, work / "tests_orig")
    rc2, out2 = pytest(args.python, ["tests_orig"], work)
    bp, bf = results(out2)
    allowed = {x for x in args.allow_changed.split(",") if x}
    regress = sorted(t for t in bf if t not in allowed)
    shutil.rmtree(work / "tests_orig", ignore_errors=True)

    outcome = "Complete" if acc_total and not f else ("Partial" if p else "Failed")
    print(json.dumps({"issue": args.issue, "outcome": outcome, "acceptance_passed": len(p),
                      "acceptance_total": acc_total, "failed_acceptance": sorted(f),
                      "regressions": len(regress), "regressed_tests": regress,
                      "baseline_passed": len(bp)}))
    for d in (tmp, hd, base):
        if d:
            shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    main()

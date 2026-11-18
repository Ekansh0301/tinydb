"""Start one recorded run and wait until it, and every round it starts, has finished.

    python experiment/drive.py 4                  # pipeline run for GitHub issue #4
    python experiment/drive.py 4 --variant single # experiment E1 on the same issue
    python experiment/drive.py 7 --round 2 --from-stage 3   # continue an issue

It only dispatches the workflow and watches; it changes nothing else. It prints one line per change
and a final summary (status, stage, reason, rounds, tokens) read from the autose-runs branch, then exits
so that a person decides what to do next (a rerun is a decision, see experiment/protocol.md).
"""
import argparse
import base64
import json
import subprocess
import sys
import time

REPO = "Ekansh0301/tinydb"


def gh(args):
    p = subprocess.run(["gh"] + args, capture_output=True, text=True)
    return p.stdout.strip(), p.returncode, p.stderr.strip()


def runs():
    out, rc, _ = gh(["run", "list", "--repo", REPO, "--workflow", "autose", "--limit", "20", "--json",
                     "databaseId,status,conclusion,event,createdAt"])
    return json.loads(out) if rc == 0 and out else []


def state(key):
    out, rc, _ = gh(["api", "repos/%s/contents/runs/issue-%s/state.json?ref=autose-runs" % (REPO, key), "--jq", ".content"])
    if rc or not out:
        return {}
    return json.loads(base64.b64decode(out))


def main():
    a = argparse.ArgumentParser()
    a.add_argument("issue", type=int)
    a.add_argument("--variant", default="pipeline")
    a.add_argument("--round", default="1")
    a.add_argument("--from-stage", default="1")
    a.add_argument("--timeout-min", type=int, default=240)
    args = a.parse_args()
    key = args.issue if args.variant == "pipeline" else "%d-%s" % (args.issue, args.variant)

    before = {r["databaseId"] for r in runs()}
    out, rc, err = gh(["workflow", "run", "autose.yml", "--repo", REPO, "-f", "issue_number=%d" % args.issue,
                       "-f", "variant=" + args.variant, "-f", "round=" + args.round, "-f", "from_stage=" + args.from_stage])
    if rc:
        sys.exit("could not start the workflow: " + err)
    print("started", args.variant, "issue", args.issue, flush=True)
    t0 = time.time()
    seen, idle_since = set(), None
    while time.time() - t0 < args.timeout_min * 60:
        time.sleep(20)
        rs = [r for r in runs() if r["databaseId"] not in before]
        for r in rs:
            tag = (r["databaseId"], r["status"], r["conclusion"])
            if tag not in seen:
                seen.add(tag)
                print(time.strftime("%H:%M:%S"), "run", r["databaseId"], r["event"], r["status"], r["conclusion"] or "", flush=True)
        active = [r for r in rs if r["status"] != "completed"]
        if rs and not active:
            idle_since = idle_since or time.time()
            if time.time() - idle_since > 90:                 # no new round was dispatched
                break
        else:
            idle_since = None
    st = state(key)
    rounds = st.get("rounds", {})
    print(json.dumps({"issue": args.issue, "variant": args.variant, "status": st.get("status"), "stage": st.get("stage"),
                      "reason": (st.get("reason") or "")[:240], "round": st.get("round"),
                      "tokens_total": st.get("tokens_total"),
                      "rounds": {k: {"status": v.get("status"), "stage": v.get("stage"), "tokens": v.get("tokens")} for k, v in rounds.items()}},
                     indent=1))


if __name__ == "__main__":
    main()

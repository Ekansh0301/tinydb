"""Total tokens used by the workflow, by model, read from the logs of every Actions run.

    python experiment/tokens.py            # writes results/tokens.csv and prints the totals

Every model call logs a line "call <provider>:<model> key#N prompt~P used T in Xs". Runs before that
logging existed (the first runs on 16 November) are not covered; their tokens are taken from the
autose-runs state files by experiment/collect.py when available and are otherwise missing, so the total is a
lower bound. Local development runs (rehearsals, probes) are not counted either.
"""
import csv
import json
import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = "Ekansh0301/tinydb"
RESULTS = Path(__file__).resolve().parents[1] / "results"
CACHE = RESULTS / "token_cache.json"
LINE = re.compile(r"call (\S+) key#\d+ prompt~\d+ used (\d+) in")


def gh(args):
    return subprocess.run(["gh"] + args, capture_output=True, text=True).stdout


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    runs = [json.loads(l) for l in gh(["api", "--paginate", "repos/%s/actions/runs?per_page=100" % REPO, "--jq", ".workflow_runs[]|@json"]).splitlines() if l.strip()]
    totals = defaultdict(lambda: defaultdict(int))
    for r in runs:
        if r["name"] not in ("autose", "review-seeded") or r["status"] != "completed":
            continue
        rid = str(r["id"])
        if rid not in cache:
            per = defaultdict(int)
            jobs = json.loads(gh(["api", "repos/%s/actions/runs/%s/jobs" % (REPO, rid)]) or "{}").get("jobs", [])
            for j in jobs:
                if j["name"] not in ("build", "review", "gate"):
                    continue
                log = gh(["api", "repos/%s/actions/jobs/%s/logs" % (REPO, j["id"])])
                for m in LINE.finditer(log):
                    per[m.group(1)] += int(m.group(2))
            cache[rid] = {"workflow": r["name"], "tokens": dict(per)}
        for model, t in cache[rid]["tokens"].items():
            totals[r["name"]][model] += t
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
    with (RESULTS / "tokens.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["workflow", "model", "tokens"])
        for wf, m in sorted(totals.items()):
            for model, t in sorted(m.items()):
                w.writerow([wf, model, t])
    grand = sum(t for m in totals.values() for t in m.values())
    print("total tokens in run logs: %d" % grand)
    for wf, m in sorted(totals.items()):
        for model, t in sorted(m.items(), key=lambda x: -x[1]):
            print("  %-14s %-60s %9d" % (wf, model, t))


if __name__ == "__main__":
    main()

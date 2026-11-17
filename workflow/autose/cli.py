"""Entry points used by the workflow jobs and for local development runs."""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path

from . import config, gitops, llm, orchestrator, review, stages
from .state import Ctx


def state_dir():
    return Path(os.environ.get("STATE_DIR") or Path(tempfile.gettempdir()) / "autose_state")


def out(**kw):
    p = os.environ.get("GITHUB_OUTPUT")
    lines = "".join("%s=%s\n" % (k, str(v).replace("\n", " ")) for k, v in kw.items())
    if p:
        open(p, "a").write(lines)
    print(lines, end="")


def injection_score(text):
    c = llm.Client("guard")
    best = 0.0
    for i in range(0, min(len(text), 6000), 1200):
        try:
            msg, _, _ = c.chat([{"role": "user", "content": text[i:i + 1200]}], max_tokens=5)
            best = max(best, float(msg.get("content") or 0))
        except Exception:
            continue
    return best


def issue_state(issue):
    try:
        raw = gitops.gh(["api", "repos/%s/contents/runs/issue-%s/state.json?ref=%s" % (config.REPO, issue, config.RUNS_BRANCH),
                         "--jq", ".content"], check=False)
        import base64
        return json.loads(base64.b64decode(raw)) if raw else {}
    except Exception:
        return {}


def cmd_gate(_):
    gitops.assert_our_repo()
    ev = json.load(open(os.environ["GITHUB_EVENT_PATH"]))
    name = os.environ["GITHUB_EVENT_NAME"]
    base = dict(go="false", issue="", round="1", from_stage="1", reason="")
    issue = sender = None
    rnd, frm = 1, 1
    extra = {}
    if name == "issues":
        if ev["action"] != "labeled" or ev["label"]["name"] != config.LABEL:
            return out(**{**base, "reason": "not the autose label"})
        issue, sender = ev["issue"]["number"], ev["sender"]["login"]
    elif name == "issue_comment":
        if ev["comment"]["body"].strip() != "/autose":
            return out(**{**base, "reason": "not a /autose comment"})
        sender = ev["comment"]["user"]["login"]
        if "pull_request" in ev["issue"]:
            pr = gitops.gh_json(["pr", "view", str(ev["issue"]["number"]), "--repo", config.REPO, "--json", "headRefName,headRefOid,state"])
            m = re.fullmatch(r"autose/issue-(\d+)", pr["headRefName"])
            if not m or pr["state"] != "OPEN":
                return out(**{**base, "reason": "not an open autose pull request"})
            issue = int(m.group(1))
            frm = 6
            st0 = issue_state(issue)
            rnd = int(st0.get("round", 1))
            extra = dict(pr=ev["issue"]["number"], sha=pr["headRefOid"], base_sha=st0.get("base_sha", ""))
        else:
            issue = ev["issue"]["number"]
    elif name == "workflow_dispatch":
        i = ev["inputs"]
        issue, sender = int(i["issue_number"]), ev["sender"]["login"]
        rnd, frm = int(i.get("round") or 1), int(i.get("from_stage") or 1)
        extra["variant"] = i.get("variant") or "pipeline"
    else:
        return out(**{**base, "reason": "unsupported event"})
    perm = gitops.gh(["api", "repos/%s/collaborators/%s/permission" % (config.REPO, sender), "--jq", ".permission"], check=False)
    if perm not in ("admin", "write", "maintain"):
        return out(**{**base, "reason": "sender %s has permission '%s'" % (sender, perm)})
    st = issue_state(issue)
    if name != "workflow_dispatch" and st.get("status") == "running" and \
            time.time() - time.mktime(time.strptime(st.get("updated", "1970-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ")) < 3 * 3600:
        gitops.gh(["issue", "comment", str(issue), "--repo", config.REPO, "--body",
                   "autose: a run for this issue is already active; ignoring this trigger."], check=False)
        return out(**{**base, "reason": "run already active"})
    data = gitops.gh_json(["issue", "view", str(issue), "--repo", config.REPO, "--json", "title,body"])
    Path("issue.json").write_text(json.dumps(data))
    if frm == 1 or rnd == 1:
        score = injection_score((data["title"] or "") + "\n" + (data["body"] or ""))
        if score >= config.INJECTION_THRESHOLD:
            gitops.gh(["issue", "comment", str(issue), "--repo", config.REPO, "--body",
                       "autose: stopped. The issue text looks like an attempt to give instructions to an automated agent "
                       "(injection score %.2f). A maintainer should review it and trigger again." % score], check=False)
            return out(**{**base, "reason": "prompt-injection score %.2f" % score})
    out(go="true", issue=issue, round=rnd, from_stage=frm, reason="ok", **{"variant": "pipeline", **extra})


def git_identity(wd):
    gitops.run(["git", "config", "user.name", "autose-bot"], wd)
    gitops.run(["git", "config", "user.email", "autose-bot@users.noreply.github.com"], wd)


def variant():
    return os.environ.get("VARIANT") or "pipeline"


def run_key(n):
    return n if variant() == "pipeline" else "%s-%s" % (n, variant())


def make_ctx(issue_no, rnd, frm, wd, runs, issue, local=False):
    branch = "autose/issue-%s" % issue_no if variant() == "pipeline" else "autose-%s/issue-%s" % (variant(), issue_no)
    st = runs.state()
    git_identity(wd)
    prev = Path(runs.root) / "runs" / ("issue-%s" % runs.issue) / ("round-%d" % (rnd - 1))
    findings = ""
    if rnd > 1 and prev.exists():
        rj = prev / "review.json"
        if rj.exists():
            js = json.loads(rj.read_text())
            findings = "\n".join("- %s:%s %s" % (f.get("file", ""), f.get("line", ""), f.get("text", ""))
                                 for f in js.get("findings") or [])[:1500]
            findings = (js.get("summary", "") + "\n" + findings).strip()
        for n in ("spec.md", "design.md"):
            if frm > (1 if n == "spec.md" else 2) and (prev / n).exists():
                runs.write(n, (prev / n).read_text())
    if frm >= 3 and rnd > 1 and not local:
        gitops.git(["fetch", "-q", "origin", branch], wd)
        gitops.run(["git", "checkout", "-q", "-B", branch, "FETCH_HEAD"], wd)
        base = st.get("base_sha") or gitops.run(["git", "rev-parse", "origin/" + config.BASE_BRANCH], wd)
    else:
        base = gitops.run(["git", "rev-parse", "HEAD"], wd)
        gitops.run(["git", "checkout", "-q", "-B", branch], wd)
    return Ctx(issue_no=issue_no, issue_title=issue["title"] or "", issue_text=issue["body"] or "",
               round_no=rnd, workdir=str(wd), base_sha=base, branch=branch, runs=runs, local=local,
               findings=findings)


def cmd_build(_):
    gitops.assert_our_repo()
    n, rnd, frm = int(os.environ["ISSUE"]), int(os.environ["ROUND"]), int(os.environ["FROM_STAGE"])
    issue = json.load(open(os.environ.get("ISSUE_FILE", "issue.json")))
    runs = gitops.Runs(state_dir(), run_key(n), rnd)
    runs.open()
    ctx = make_ctx(n, rnd, frm, os.getcwd(), runs, issue)
    runs.write("run.json", json.dumps({
        "run_id": os.environ.get("GITHUB_RUN_ID"), "attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "event": os.environ.get("GITHUB_EVENT_NAME"), "issue": n, "variant": variant(), "round": rnd,
        "from_stage": frm, "base_sha": ctx.base_sha, "branch": ctx.branch,
        "started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, indent=1))
    res = orchestrator.build_single(ctx) if variant() == "single" else orchestrator.build(ctx, frm)
    out(status=res["status"], pr=res.get("pr", ""), sha=res.get("sha", ""), base_sha=ctx.base_sha)
    runs.write("log.txt", "\n".join(ctx.log_lines) + "\n")
    runs.persist("autose: issue %d round %d log" % (n, rnd))
    if res["status"] != "RELEASED":
        gitops.gh(["issue", "comment", str(n), "--repo", config.REPO, "--body",
                   "autose: stopped at stage %s. %s\nArtifacts: https://github.com/%s/tree/%s/runs/issue-%s/round-%d" %
                   (res["stage"], res["reason"][:600], config.REPO, config.RUNS_BRANCH, run_key(n), rnd)], check=False)


def cmd_review(_):
    gitops.assert_our_repo()
    issue = json.load(open(os.environ.get("ISSUE_FILE", "issue.json")))
    outdir = Path(os.environ.get("REVIEW_DIR", "review_out"))
    outdir.mkdir(exist_ok=True)
    js, why, client, res = review.run_review(os.getcwd(), os.environ["BASE_SHA"], issue["title"] or "", issue["body"] or "")
    tier = ", ".join(sorted(set(client.served))) or "none"
    meta = {"tiers": client.served, "tokens": client.tokens_used, "calls": client.calls, "problems": why,
            "run_id": os.environ.get("GITHUB_RUN_ID")}
    (outdir / "meta.json").write_text(json.dumps(meta))
    (outdir / "transcript_6.jsonl").write_text("\n".join(json.dumps(x) for x in getattr(client, "last_transcript", [])))
    if js is None or why:
        (outdir / "review.md").write_text("# Review\n\nNo valid review was produced: %s\n" % "; ".join(why))
        out(verdict="NONE")
        return
    (outdir / "review.json").write_text(json.dumps(js))
    (outdir / "review.md").write_text(review.render(js, tier))
    out(verdict=js["verdict"], issue_class=js.get("issue_class") or "")


def dispatch(n, rnd, frm):
    gitops.gh(["workflow", "run", "autose.yml", "--repo", config.REPO, "-f", "issue_number=%d" % n,
               "-f", "round=%d" % rnd, "-f", "from_stage=%d" % frm])


def cmd_next(_):
    gitops.assert_our_repo()
    n, rnd = int(os.environ["ISSUE"]), int(os.environ["ROUND"])
    pr, build_res, ci_res = os.environ.get("PR", ""), os.environ.get("BUILD_RESULT", ""), os.environ.get("CI_RESULT", "")
    runs = gitops.Runs(state_dir(), run_key(n), rnd)
    runs.open()
    ro = Path(os.environ.get("REVIEW_DIR", "review_out"))
    for f in ("review.md", "review.json", "meta.json", "transcript_6.jsonl"):
        if (ro / f).exists():
            runs.write(f, (ro / f).read_text())
    base_url = "https://github.com/%s/tree/%s/runs/issue-%s/round-%d" % (config.REPO, config.RUNS_BRANCH, run_key(n), rnd)

    def final(status, text, comment=True):
        st = runs.state()
        st.update({"status": status, "round": rnd, "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        runs.save_state(st)
        runs.persist("autose: issue %d round %d %s" % (n, rnd, status))
        if comment:
            gitops.gh(["issue", "comment", str(n), "--repo", config.REPO, "--body", text + "\n\nArtifacts: " + base_url], check=False)
        print(status, text)

    if build_res not in ("success", "skipped") or not pr:
        return final("STOPPED", "the build job stopped before a pull request was ready", comment=False)
    if ci_res != "success":
        gitops.gh(["pr", "comment", pr, "--repo", config.REPO, "--body", "autose: CI did not pass; no review was requested."], check=False)
        return final("STOPPED", "autose: CI failed on pull request #%s; the run stopped." % pr)
    js = json.loads((ro / "review.json").read_text()) if (ro / "review.json").exists() else None
    body = (ro / "review.md").read_text() if (ro / "review.md").exists() else "# Review\n\nNo review was produced.\n"
    gitops.gh(["pr", "comment", pr, "--repo", config.REPO, "--body", body], check=False)
    if js is None:
        return final("REVIEW_UNAVAILABLE", "autose: no valid review was produced, so there is no approval. A person must review pull request #%s." % pr)
    if js["verdict"] == "APPROVE":
        return final("DONE", "autose: reviewer approved pull request #%s. Merge or close is a human decision." % pr)
    if variant() != "pipeline":
        return final("DONE", "autose (%s variant): review recorded for pull request #%s; the experiment ends after round 1." % (variant(), pr))
    if rnd - 1 >= config.MAX_FIX_CYCLES:
        return final("DONE", "autose: the reviewer still asks for changes after %d fix cycles. Pull request #%s is left for a human decision." % (config.MAX_FIX_CYCLES, pr))
    frm = 2 if js.get("issue_class") == "approach" else 3
    st = runs.state()
    st.update({"status": "running", "round": rnd + 1})
    runs.save_state(st)
    runs.persist("autose: issue %d round %d review requested changes (%s)" % (n, rnd, js.get("issue_class")))
    dispatch(n, rnd + 1, frm)
    print("dispatched round %d from stage %d" % (rnd + 1, frm))


def cmd_local(a):
    """Development run on a local clone: stages 1-4, no push, no pull request."""
    src = Path(a.repo).resolve()
    tmp = Path(tempfile.mkdtemp(prefix="autose-local-"))
    wd = tmp / "work"
    gitops.run(["git", "clone", "-q", "--no-hardlinks", str(src), str(wd)])
    text = Path(a.issue).read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    issue = {"title": title, "body": "\n".join(text.splitlines()[1:]).strip()}
    runs = gitops.Runs(tmp / "runs", a.number, 1)
    runs.open(remote=False)
    ctx = make_ctx(a.number, 1, 1, wd, runs, issue, local=True)
    res = orchestrator.build(ctx, a.from_stage)
    print(json.dumps(res), "tokens", ctx.tokens, "calls", ctx.calls)
    print("artifacts:", runs.dir, "\nworkdir:", wd)
    if a.review and res["status"] == "RELEASED":
        js, why, client, rr = review.run_review(str(wd), ctx.base_sha, issue["title"], issue["body"])
        print("REVIEW", json.dumps(js, indent=1) if js else why, "\ntiers", sorted(set(client.served)))


def cmd_record(_):
    """Store a calibration review (seeded pull request) on the runs branch and say so on the PR."""
    gitops.assert_our_repo()
    pr, variant, trial, run_id = os.environ["PR"], os.environ["VARIANT"], os.environ["TRIAL"], os.environ["RUN_ID"]
    runs = gitops.Runs(state_dir(), 0, 0)
    runs.open()
    runs.dir = runs.root / "runs" / "seeded" / ("pr-%s" % pr) / ("%s-t%s-run%s" % (variant, trial, run_id))
    ro = Path(os.environ.get("REVIEW_DIR", "review_out"))
    verdict = "NONE"
    for f in ("review.json", "review.md", "meta.json", "transcript_6.jsonl"):
        if (ro / f).exists():
            runs.write(f, (ro / f).read_text())
    if (ro / "review.json").exists():
        verdict = json.loads((ro / "review.json").read_text()).get("verdict", "NONE")
    runs.write("verdict.txt", verdict + "\n")
    runs.persist("autose: calibration review pr %s %s trial %s -> %s" % (pr, variant, trial, verdict))
    body = (ro / "review.md").read_text() if (ro / "review.md").exists() else "# Review\n\nNo valid review was produced.\n"
    gitops.gh(["pr", "comment", pr, "--repo", config.REPO, "--body",
               "Calibration review (variant `%s`, trial %s, run %s)\n\n%s" % (variant, trial, run_id, body)], check=False)
    print("recorded", pr, variant, trial, verdict)


def main():
    p = argparse.ArgumentParser(prog="autose")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("gate", cmd_gate), ("build", cmd_build), ("review", cmd_review), ("next", cmd_next), ("record", cmd_record)):
        sub.add_parser(name).set_defaults(fn=fn)
    lc = sub.add_parser("local")
    lc.add_argument("--issue", required=True)
    lc.add_argument("--repo", default=".")
    lc.add_argument("--number", type=int, default=1)
    lc.add_argument("--from-stage", type=int, default=1)
    lc.add_argument("--review", action="store_true")
    lc.set_defaults(fn=cmd_local)
    a = p.parse_args()
    a.fn(a)

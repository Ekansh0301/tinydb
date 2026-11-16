"""The state machine (ADR-002). Rules are code: a stage moves forward only when
its gate passes; back-edges and attempt limits are fixed here."""
from . import config, gitops, stages

LIMITS = {"s1": 2, "s2": 2, "impl": 3, "tests": 3, "redesign": 1}


def stop(ctx, stage, reasons):
    msg = "; ".join(reasons) or "no reason recorded"
    name = {"1": "spec.md", "2": "design.md", "3": "diff.patch", "4": "test_report.md", "5": "pr.md"}.get(str(stage), "state.json")
    old = ctx.runs.read(name, "") or ""
    ctx.runs.write(name, old + "\n\n## Stopped\nStage %s could not pass its check: %s\n" % (stage, msg))
    ctx.snapshot(str(stage), "STOPPED", msg)
    ctx.log("STOPPED at stage %s: %s" % (stage, msg))
    return {"status": "STOPPED", "stage": str(stage), "reason": msg}


def sanitize(ctx):
    """Delete untracked files that are neither named in the design nor the tester's file,
    so stray test output can never reach the pull request."""
    import re
    from . import gates
    allowed = gates.design_files(ctx.runs.read("design.md", "") or "")
    for f in gitops.run(["git", "ls-files", "--others", "--exclude-standard"], ctx.workdir).splitlines():
        if f in allowed or re.fullmatch(r"tests/test_autose_\w+\.py", f):
            continue
        ctx.log("removing stray file: " + f)
        gitops.run(["rm", "-rf", f], ctx.workdir, check=False)


def commit_code(ctx, message):
    sanitize(ctx)
    gitops.run(["git", "add", "-u"], ctx.workdir)        # tracked files that changed
    for f in gitops.run(["git", "ls-files", "--others", "--exclude-standard"], ctx.workdir).splitlines():
        gitops.run(["git", "add", "--", f], ctx.workdir)   # new files: sanitize kept only allowed ones
    if gitops.run(["git", "status", "--porcelain"], ctx.workdir):
        gitops.run(["git", "commit", "-q", "-m", message], ctx.workdir)


def build(ctx, from_stage):
    ctx.snapshot(str(from_stage), "running")
    stage, notes = from_stage, []
    while True:
        ctx.persist()
        if stage == 1:
            ctx.log("stage 1 requirements")
            o = stages.stage1(ctx, notes)
            if o.ok:
                stage, notes = 2, []
                continue
            if ctx.bump("s1") >= LIMITS["s1"]:
                return stop(ctx, 1, o.reasons)
            notes = o.reasons
        elif stage == 2:
            ctx.log("stage 2 design")
            o = stages.stage2(ctx, notes)
            if o.ok:
                stage, notes = 3, []
                continue
            if ctx.bump("s2") >= LIMITS["s2"]:
                return stop(ctx, 2, o.reasons)
            notes = o.reasons
        elif stage == 3:
            ctx.log("stage 3 implementation (attempt %d)" % (ctx.counters.get("impl", 0) + 1))
            o = stages.stage3(ctx, notes)
            if o.ok:
                commit_code(ctx, "autose: implement #%d" % ctx.issue_no)
                stage, notes = 4, []
                continue
            if ctx.bump("impl") >= LIMITS["impl"]:
                return stop(ctx, 3, o.reasons)
            notes = o.reasons
        elif stage == 4:
            ctx.log("stage 4 testing (attempt %d)" % (ctx.counters.get("tests", 0) + 1))
            o = stages.stage4(ctx, notes)
            if o.ok:
                commit_code(ctx, "autose: tests for #%d" % ctx.issue_no)
                stage = 5
                continue
            if o.route == "impl":
                failing = o.data.get("failed", [])
                for t in failing:
                    import re
                    m = re.search(r"test_ac(\d+)_", t)
                    if m:
                        ctx.bump("ac" + m.group(1) + "_fail")
                repeated = any(k.startswith("ac") and v >= 2 for k, v in ctx.counters.items())
                if repeated and ctx.counters.get("redesign", 0) < LIMITS["redesign"]:
                    ctx.bump("redesign")
                    ctx.log("same criterion failed twice: back to design")
                    for k in [k for k in ctx.counters if k.startswith("ac")]:
                        ctx.counters[k] = 0
                    ctx.counters["s2"] = ctx.counters["impl"] = 0
                    stage = 2
                    notes = ["The implementation could not satisfy these tests: " + ", ".join(failing[:6]) +
                             ". The plan may be wrong or incomplete; revise it."]
                    gitops.run(["git", "reset", "-q", "--hard", ctx.base_sha], ctx.workdir)
                    gitops.run(["git", "clean", "-fdq"], ctx.workdir)
                    continue
                if ctx.bump("impl") >= LIMITS["impl"]:
                    return stop(ctx, 4, o.reasons)
                stage, notes = 3, o.reasons
                continue
            if ctx.bump("tests") >= LIMITS["tests"]:
                return stop(ctx, 4, o.reasons)
            notes = o.reasons
        elif stage == 5:
            ctx.log("stage 5 release")
            try:
                o = stages.stage5(ctx)
            except Exception as e:
                return stop(ctx, 5, [str(e)[:300]])
            ctx.runs.write("result.json", __import__("json").dumps(o.data))
            ctx.snapshot("5", "released")
            ctx.persist()
            return {"status": "RELEASED", "pr": o.data.get("pr"), "sha": o.data.get("sha")}

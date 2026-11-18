"""The state machine (ADR-002). Rules are code: a stage moves forward only when
its gate passes; back-edges and attempt limits are fixed here."""
from . import config, gitops, stages

LIMITS = {"s1": 3, "s2": 3, "impl": 3, "tests": 3, "redesign": 1}


def record(ctx, stage, outcome):
    """One line per stage attempt: the evidence for per-stage pass rates (results/results.csv)."""
    import json
    import time
    ctx.runs.append("stages.jsonl", json.dumps({
        "run_id": __import__("os").environ.get("GITHUB_RUN_ID"), "round": ctx.round_no, "stage": stage, "ok": bool(outcome.ok), "route": getattr(outcome, "route", ""),
        "reasons": [str(r)[:200] for r in outcome.reasons[:6]], "tokens_so_far": ctx.tokens,
        "calls_so_far": ctx.calls, "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}) + "\n")


def budget_spent(outcome):
    """The run's token budget is gone: retrying cannot help, so the run stops at once."""
    return (not outcome.ok) and any("run token budget" in r for r in outcome.reasons)


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


def discard_changes(ctx):
    """Back to the last commit (the base, or the head of the pull request in a later round)."""
    try:
        gitops.run(["git", "reset", "-q", "--hard", "HEAD"], ctx.workdir, check=False)
        gitops.run(["git", "clean", "-fdq"], ctx.workdir, check=False)
    except OSError:
        return
    ctx.log("discarded partial edits")


def commit_code(ctx, message):
    sanitize(ctx)
    gitops.run(["git", "add", "-u"], ctx.workdir)        # tracked files that changed
    for f in gitops.run(["git", "ls-files", "--others", "--exclude-standard"], ctx.workdir).splitlines():
        gitops.run(["git", "add", "--", f], ctx.workdir)   # new files: sanitize kept only allowed ones
    if gitops.run(["git", "status", "--porcelain"], ctx.workdir):
        gitops.run(["git", "commit", "-q", "-m", message], ctx.workdir)


def guarded(fn, *args):
    """A bug in a stage or a gate must end as a recorded stop with its reason, never as a dead job."""
    try:
        return fn(*args)
    except Exception as e:                                   # noqa: BLE001
        return stages.Outcome(False, ["internal error in %s: %s: %s" % (fn.__name__, type(e).__name__, str(e)[:160])])


def build(ctx, from_stage):
    ctx.snapshot(str(from_stage), "running")
    stage, notes = from_stage, []
    while True:
        ctx.persist()
        if stage == 1:
            ctx.log("stage 1 requirements")
            o = guarded(stages.stage1, ctx, notes)
            record(ctx, 1, o)
            if budget_spent(o) or any(r.startswith("internal error") for r in o.reasons):
                return stop(ctx, 1, o.reasons)
            if o.ok:
                stage, notes = 2, []
                continue
            if ctx.bump("s1") >= LIMITS["s1"]:
                return stop(ctx, 1, o.reasons)
            notes = o.reasons
        elif stage == 2:
            ctx.log("stage 2 design")
            o = guarded(stages.stage2, ctx, notes)
            record(ctx, 2, o)
            if budget_spent(o) or any(r.startswith("internal error") for r in o.reasons):
                return stop(ctx, 2, o.reasons)
            if o.ok:
                stage, notes = 3, []
                continue
            if ctx.bump("s2") >= LIMITS["s2"]:
                return stop(ctx, 2, o.reasons)
            notes = o.reasons
        elif stage == 3:
            ctx.log("stage 3 implementation (attempt %d)" % (ctx.counters.get("impl", 0) + 1))
            o = guarded(stages.stage3, ctx, notes)
            record(ctx, 3, o)
            if budget_spent(o) or any(r.startswith("internal error") for r in o.reasons):
                return stop(ctx, 3, o.reasons)
            if o.ok:
                commit_code(ctx, "autose: implement #%d" % ctx.issue_no)
                stage, notes = 4, []
                continue
            if any("model unavailable" in r for r in o.reasons):
                discard_changes(ctx)       # a model that vanished mid-edit leaves a half-written file
            if ctx.bump("impl") >= LIMITS["impl"]:
                return stop(ctx, 3, o.reasons)
            notes = o.reasons
        elif stage == 4:
            ctx.log("stage 4 testing (attempt %d)" % (ctx.counters.get("tests", 0) + 1))
            o = guarded(stages.stage4, ctx, notes)
            record(ctx, 4, o)
            if budget_spent(o) or any(r.startswith("internal error") for r in o.reasons):
                return stop(ctx, 4, o.reasons)
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
                    ctx.log("same criterion failed twice: back to requirements")
                    for k in [k for k in ctx.counters if k.startswith("ac")]:
                        ctx.counters[k] = 0
                    ctx.counters["s1"] = ctx.counters["s2"] = ctx.counters["impl"] = 0
                    stage = 1
                    notes = ["The implementation could not satisfy these tests: " + ", ".join(failing[:6]) +
                             ". A criterion may ask for something the code does not offer (for example a parameter that does not exist); "
                             "check each criterion against the real API and revise the specification."]
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


def build_single(ctx):
    """Experiment E1: one agent, three attempts, then the same release step."""
    ctx.snapshot("single", "running")
    notes = []
    for attempt in range(3):
        ctx.persist()
        ctx.log("single agent (attempt %d)" % (attempt + 1))
        o = stages.stage_single(ctx, notes)
        record(ctx, "single", o)
        ctx.runs.write("single_attempt_%d.json" % (attempt + 1), __import__("json").dumps(
            {"ok": o.ok, "gates": o.data.get("gates"), "reasons": o.reasons}))
        if o.ok:
            commit_code(ctx, "autose(single): implement #%d" % ctx.issue_no)
            try:
                r = stages.stage5(ctx)
            except Exception as e:
                return stop(ctx, 5, [str(e)[:300]])
            ctx.runs.write("result.json", __import__("json").dumps(r.data))
            ctx.snapshot("5", "released")
            ctx.persist()
            return {"status": "RELEASED", "pr": r.data.get("pr"), "sha": r.data.get("sha")}
        notes = o.reasons[:8]
        if o.data.get("gates", [True] * 4)[2] is False:
            discard_changes(ctx)        # the code does not even compile or import: start the next attempt from a clean tree
    return stop(ctx, "single", notes)

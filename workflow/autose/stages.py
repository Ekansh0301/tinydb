"""The stages. Each one runs an agent (or code), writes its artifact and returns
an Outcome decided by a gate. Stages never choose what happens next."""
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import agent, config, gates, gitops, llm, tools

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


@dataclass
class Outcome:
    ok: bool
    reasons: list = field(default_factory=list)
    route: str = ""           # for stage 4: "tests", "impl" or "design"
    data: dict = field(default_factory=dict)


def prompt(name):
    return (PROMPTS / name).read_text()


def untrusted(ctx):
    text = ctx.issue_text[:4000].replace("</untrusted_issue>", "")
    return "<untrusted_issue>\nTitle: %s\n\n%s\n</untrusted_issue>" % (ctx.issue_title[:200].replace("</untrusted_issue>", ""), text)


def strip_fences(t):
    t = t.strip()
    m = re.match(r"^```[a-zA-Z]*\n(.*)\n```$", t, re.S)
    return m.group(1).strip() if m else t


def account(ctx, client, res):
    ctx.tokens += res.tokens
    ctx.calls += res.calls
    ctx.tiers += client.served
    client.served = []
    ctx.runs.write("transcript_%s.jsonl" % ctx.cur_stage, "\n".join(json.dumps(x) for x in res.transcript))


def check_budget(ctx):
    if ctx.tokens > config.BUDGET["run_tokens"]:
        return Outcome(False, ["run token budget (%d) exhausted" % config.BUDGET["run_tokens"]])
    return None


def notes_block(notes):
    return ("\n\nProblems found in the previous attempt (fix exactly these):\n- " + "\n- ".join(notes)) if notes else ""


# -- 1 requirements ----------------------------------------------------------
def stage1(ctx, notes):
    ctx.cur_stage = "1"
    over = check_budget(ctx)
    if over:
        return over
    c = llm.Client("planner", ctx.log)
    tb = tools.Toolbox(ctx.workdir, "planner")
    user = untrusted(ctx) + notes_block(notes)
    if ctx.findings:
        user += "\n\nA reviewer found these problems with an earlier attempt; the specification may need to cover them:\n" + ctx.findings
    res = agent.run_agent("planner", c, prompt("spec.md"), user, tb, max_tokens=1700)
    account(ctx, c, res)
    if res.stopped:
        return Outcome(False, ["agent stopped: " + res.stopped])
    spec = strip_fences(res.text)
    ctx.runs.write("spec.md", spec + "\n")
    ok, why = gates.gate_spec(spec)
    if ok:
        bad = testability_check(ctx, spec)
        if bad:
            ok, why = False, bad
    return Outcome(ok, why)


def testability_check(ctx, spec):
    """Second, short model call that flags criteria an automated test could not check."""
    acs = gates.parse_acs(spec)
    listing = "\n".join("AC-%d: %s" % (n, t) for n, t in acs.items())
    c = llm.Client("planner", ctx.log)
    try:
        msg, used, _ = c.chat([
            {"role": "system", "content": "You check acceptance criteria. A criterion is NOT testable if an automated test "
             "cannot decide pass or fail from it (vague outcome, no concrete value, depends on opinion). "
             "Answer with JSON only: {\"not_testable\": [<numbers>]}"},
            {"role": "user", "content": listing[:3000]}], max_tokens=400)
        ctx.tokens += used
        ctx.calls += 1
        m = re.search(r"\{.*\}", msg.get("content") or "", re.S)
        ids = json.loads(m.group(0)).get("not_testable", []) if m else []
        return ["AC-%s is judged not testable by an automated test" % i for i in ids if str(i).isdigit()]
    except Exception as e:                     # the structural gate already passed
        ctx.log("testability check skipped: %s" % e)
        return []


def arch_for_design(arch):
    """Components, ADR titles with their decisions, and the constraints. The longer
    ADR text is dropped so the request stays under the model's rate limit (ADR-011)."""
    parts = re.split(r"\n(?=## )", arch)
    keep = []
    for part in parts:
        if re.match(r"## 2\.", part):
            head = part.splitlines()[0]
            adrs = re.findall(r"### (ADR-\d+:[^\n]*)\n(?:.*\n)*?- \*\*Decision:\*\* ([^\n]*(?:\n  [^\n]*)*)", part)
            keep.append(head + "\n" + "\n".join("- %s. Decision: %s" % (t.strip(), " ".join(d.split())) for t, d in adrs))
        else:
            keep.append(part)
    return "\n".join(keep)


# -- 2 design -------------------------------------------------------------------
def stage2(ctx, notes):
    ctx.cur_stage = "2"
    over = check_budget(ctx)
    if over:
        return over
    spec = ctx.runs.read("spec.md", "")
    arch = arch_for_design((Path(ctx.workdir) / "ARCHITECTURE.md").read_text())
    c = llm.Client("planner", ctx.log)
    tb = tools.Toolbox(ctx.workdir, "planner")
    user = "SPECIFICATION\n" + spec + "\n\nARCHITECTURE NOTES\n" + arch + notes_block(notes)
    if ctx.findings:
        user += "\n\nA reviewer found these problems with an earlier attempt (change the plan so they are avoided):\n" + ctx.findings
    res = agent.run_agent("planner", c, prompt("design.md"), user, tb, input_budget=5600, max_tokens=1500)
    account(ctx, c, res)
    if res.stopped:
        return Outcome(False, ["agent stopped: " + res.stopped])
    design = strip_fences(res.text)
    ctx.runs.write("design.md", design + "\n")
    ok, why = gates.gate_design(design, spec, ctx.workdir)
    return Outcome(ok, why)


# -- 3 implementation ---------------------------------------------------------
def stage3(ctx, notes):
    ctx.cur_stage = "3"
    over = check_budget(ctx)
    if over:
        return over
    spec, design = ctx.runs.read("spec.md", ""), ctx.runs.read("design.md", "")
    c = llm.Client("implementer", ctx.log)
    tb = tools.Toolbox(ctx.workdir, "implementer")
    user = "SPECIFICATION\n" + spec + "\n\nDESIGN\n" + design + notes_block(notes)
    if ctx.findings and not notes:
        user += "\n\nA reviewer found these problems in the current code; fix them:\n" + ctx.findings
    res = agent.run_agent("implementer", c, prompt("implementer.md"), user, tb, input_budget=5500)
    account(ctx, c, res)
    ok, why = gates.gate_impl(ctx.workdir, ctx.base_sha, design)
    diff = gitops.run(["git", "diff", ctx.base_sha], ctx.workdir, check=False)
    ctx.runs.write("diff.patch", diff + "\n")
    if res.stopped and not ok:
        why = ["agent stopped: " + res.stopped] + why
    return Outcome(ok, why)


# -- 4 testing ----------------------------------------------------------------
def stage4(ctx, notes):
    ctx.cur_stage = "4"
    over = check_budget(ctx)
    if over:
        return over
    spec, design = ctx.runs.read("spec.md", ""), ctx.runs.read("design.md", "")
    files = sorted(gates.design_files(design))
    c = llm.Client("tester", ctx.log)
    tb = tools.Toolbox(ctx.workdir, "tester")
    user = "SPECIFICATION\n" + spec + "\n\nFiles that were changed (names only): " + ", ".join(files) + notes_block(notes)
    res = agent.run_agent("tester", c, prompt("tester.md"), user, tb, input_budget=5500)
    account(ctx, c, res)
    if res.stopped and not gates.test_names(ctx.workdir):
        return Outcome(False, ["agent stopped: " + res.stopped], route="tests")
    ok, why, rep = gates.gate_tests(ctx.workdir, ctx.base_sha, spec)
    write_test_report(ctx, ok, why, rep)
    if ok:
        return Outcome(True, [], data=rep)
    suite_failed = [w for w in why if w.startswith("test suite does not pass")]
    route = "impl" if suite_failed else "tests"
    return Outcome(False, why + ([("failing: " + ", ".join(rep.get("failed", [])[:6]))] if rep.get("failed") else []),
                   route=route, data=rep)


def write_test_report(ctx, ok, why, rep):
    lines = ["# Test report", "", "Result: **%s**" % ("PASS" if ok else "FAIL"), ""]
    lines.append("New tests: " + ", ".join(n for n, _ in gates.test_names(ctx.workdir)))
    lines.append("")
    lines.append("- Failing on the base commit (expected for new behaviour): %s" % (", ".join(rep.get("base_failed", [])) or "none"))
    lines.append("- Tests passing on the new code: %s" % rep.get("passed", "?"))
    lines.append("- Failing on the new code: %s" % (", ".join(rep.get("failed", [])) or "none"))
    if why:
        lines += ["", "Gate findings:"] + ["- " + w for w in why]
    out = rep.get("suite_output", "")
    lines += ["", "Last lines of the full suite run:", "```", out[-900:], "```"]
    ctx.runs.write("test_report.md", "\n".join(lines) + "\n")


# -- 5 release ---------------------------------------------------------------
def pr_body(ctx):
    spec = ctx.runs.read("spec.md", "")
    acs = gates.parse_acs(spec)
    files = gitops.run(["git", "diff", "--stat", ctx.base_sha], ctx.workdir, check=False)
    rep = ctx.runs.read("test_report.md", "")
    base = "https://github.com/%s/tree/%s/runs/issue-%s/round-%s" % (config.REPO, config.RUNS_BRANCH, ctx.issue_no, ctx.round_no)
    return "\n".join([
        "Refs #%d (round %d)" % (ctx.issue_no, ctx.round_no), "",
        "## Acceptance criteria", *["- AC-%d: %s" % (n, t) for n, t in acs.items()], "",
        "## Changes", "```", files, "```", "",
        "## Tests", rep.split("Last lines")[0].strip(), "",
        "## Process", "Spec, design, test report and review are in [%s](%s). Tokens used so far: %d." % (config.RUNS_BRANCH, base, ctx.tokens),
        "", "Opened by the autose workflow. It never merges; a person decides."])


def stage5(ctx):
    ctx.cur_stage = "5"
    body = pr_body(ctx)
    ctx.runs.write("pr.md", body + "\n")
    if ctx.local:
        return Outcome(True, [], data={"pr": None, "sha": gitops.run(["git", "rev-parse", "HEAD"], ctx.workdir)})
    gitops.git(["push", "--force-with-lease", "origin", "HEAD:refs/heads/" + ctx.branch], ctx.workdir)
    sha = gitops.run(["git", "rev-parse", "HEAD"], ctx.workdir)
    existing = gitops.gh_json(["pr", "list", "--repo", config.REPO, "--head", ctx.branch, "--state", "open", "--json", "number"]) or []
    if existing:
        n = existing[0]["number"]
        gitops.gh(["pr", "edit", str(n), "--repo", config.REPO, "--body", body])
    else:
        url = gitops.gh(["pr", "create", "--repo", config.REPO, "--base", config.BASE_BRANCH, "--head", ctx.branch,
                         "--title", "autose: " + ctx.issue_title[:80] + " (#%d)" % ctx.issue_no, "--body", body])
        n = int(url.rstrip("/").split("/")[-1])
    ctx.runs.write("pr_link.txt", "https://github.com/%s/pull/%d\nhead %s\n" % (config.REPO, n, sha))
    return Outcome(True, [], data={"pr": n, "sha": sha})

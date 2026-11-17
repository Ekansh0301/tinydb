"""Stage 6. The reviewer sees only the issue, the diff and the repository at the
pull request head (ADR-003, ADR-008). It has no write token; its verdict leaves
this job as a file and the next job acts on it."""
import json
import re

from . import agent, config, gates, gitops, llm, stages, tools


def parse_json(text):
    text = stages.strip_fences(text or "")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except ValueError:
        return None


def render(js, tier_note):
    lines = ["# Review", "", "Verdict: **%s**" % js.get("verdict", "NONE")]
    if js.get("issue_class"):
        lines.append("Problem class: %s" % js["issue_class"])
    lines += ["", js.get("summary", ""), "", "## Checks"]
    for c in js.get("checks") or []:
        lines.append("- [%s] %s: %s" % (c.get("result", "?"), c.get("claim", ""), str(c.get("evidence", ""))[:300]))
    lines += ["", "## Findings"]
    for f in js.get("findings") or []:
        lines.append("- (%s) %s:%s %s" % (f.get("severity", "?"), f.get("file", ""), f.get("line", ""), f.get("text", "")))
    lines += ["", "_Reviewer model: %s_" % tier_note]
    return "\n".join(lines) + "\n"


def run_review(workdir, base_sha, issue_title, issue_text, log=print):
    diff = gitops.run(["git", "diff", base_sha, "HEAD"], workdir, check=False)
    cut = diff[:8000] + ("\n[diff truncated; read the files with your tools]" if len(diff) > 8000 else "")
    text = issue_text[:3000].replace("</untrusted_issue>", "")
    user = "<untrusted_issue>\nTitle: %s\n\n%s\n</untrusted_issue>\n\nDIFF\n%s" % (issue_title[:200], text, cut)
    c = llm.Client("reviewer", log)
    tb = tools.Toolbox(workdir, "reviewer")
    notes = ""
    for attempt in range(2):
        res = agent.run_agent("reviewer", c, stages.prompt("reviewer.md"), user + notes, tb, input_budget=6000,
                              stage_calls=24, stage_tokens=150_000, wrap_up_at=0.6)
        js = parse_json(res.text)
        c.last_transcript = res.transcript
        if res.stopped and js is None:
            return None, ["reviewer stopped: " + res.stopped], c, res
        ok, why = gates.gate_review(js, tb.ran_command)
        if ok:
            return js, [], c, res
        notes = "\n\nYour last answer was rejected: " + "; ".join(why) + ". Fix this and answer again."
    return js, why, c, res

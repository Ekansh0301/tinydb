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
    """One review. If the first tier gives an invalid review (no JSON, no evidence, budget used up) the
    review is retried once on the next tier (ADR-012); a second invalid review means no review."""
    diff = gitops.run(["git", "diff", base_sha, "HEAD"], workdir, check=False)
    cut = diff[:8000] + ("\n[diff truncated; read the files with your tools]" if len(diff) > 8000 else "")
    text = issue_text[:3000].replace("</untrusted_issue>", "")
    user = "<untrusted_issue>\nTitle: %s\n\n%s\n</untrusted_issue>\n\nDIFF\n%s" % (issue_title[:200], text, cut)
    all_tiers = config.tiers("reviewer")
    attempts = []
    last = None
    for start in range(min(2, len(all_tiers))):
        c = llm.Client("reviewer", log, tiers=all_tiers[start:])
        tb = tools.Toolbox(workdir, "reviewer")
        js, why, res = one_review(c, tb, user)
        attempts.append({"tier": ",".join(sorted(set(c.served))) or "none", "ok": not why, "problems": why, "tokens": c.tokens_used})
        c.attempts = attempts
        last = (js, why, c, res)
        if not why:
            return last
        log("review attempt %d invalid (%s); %s" % (start + 1, "; ".join(why)[:160], "trying the next tier" if start == 0 else "no review"))
    return last


def one_review(c, tb, user):
    res = agent.run_agent("reviewer", c, stages.prompt("reviewer.md"), user, tb, input_budget=6000, max_tokens=2000,
                          stage_calls=24, stage_tokens=150_000, wrap_up_at=0.6)
    c.last_transcript = res.transcript
    js = parse_json(res.text)
    if js is None and res.text and not res.stopped:
        # the analysis is there but not in the required format: ask for the same findings as the JSON object
        res.text = reformat(c, user, res.text)
        js = parse_json(res.text)
    if res.stopped and js is None:
        return None, ["reviewer stopped: " + res.stopped], res
    ok, why = gates.gate_review(js, tb.ran_command)
    return js, ([] if ok else why), res


def reformat(client, user, analysis):
    msgs = [{"role": "system", "content": stages.prompt("reviewer.md")}, {"role": "user", "content": user[:6000]},
            {"role": "assistant", "content": analysis[:6000]},
            {"role": "user", "content": "Now give your result as the single JSON object described in the instructions, and nothing else. "
                                        "Use only what is already in your analysis; every check needs the evidence you already gathered."}]
    try:
        msg, _, _ = client.chat(msgs, None, max_tokens=1500, temperature=0.1)
        return msg.get("content") or ""
    except llm.LLMError:
        return ""

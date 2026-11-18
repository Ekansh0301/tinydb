"""Write report/generated/*.tex from the results tables and build report.pdf.

    python report/build.py          # needs results/*.csv (python experiment/collect.py)
"""
import csv
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).resolve().parent
ROOT = R.parent
GEN = R / "generated"
GEN.mkdir(exist_ok=True)


def tex(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")
             .replace("#", r"\#").replace("$", r"\$"))


def rows(name):
    f = ROOT / "results" / name
    return list(csv.DictReader(f.open())) if f.exists() else []


# ---- static tables -----------------------------------------------------------------------------------
STAGES = r"""
\begin{table}[ht]\centering\small
\caption{Stage map: agent, artifact and check. A gate is decided by code (\adr{007}); an agent never says ``done''.}\label{tab:stages}
\begin{tabularx}{\linewidth}{@{}c l l l Y@{}}
\toprule
\# & Stage & Agent (model) & Artifact & Check before moving on \\ \midrule
1 & Requirements & Planner (\code{gpt-oss-120b}), A1 skill & \code{spec.md} & required sections; every criterion Given/When/Then with a concrete outcome; no vague word; each requirement has a criterion; one model call may only add ``not testable'' objections \\
2 & Design & Planner (same), A2 architecture note & \code{design.md} & every file and function named exists or is marked NEW; every criterion appears in a row \\
3 & Implementation & Implementer (\code{gpt-oss-120b}) & \code{diff.patch} & diff not empty; only files named in the design changed; compiles and imports \\
4 & Testing & Tester (\code{gpt-oss-20b}) & \code{test\_report.md} & a test \code{test\_ac<N>\_*} per criterion; at least one new test fails on the base commit; whole suite passes; fails go back to 3, a repeated failure to 1 \\
5 & Release & none (code) & \code{pr.md} + PR link & PR open; reusable CI workflow green on its head \\
6 & Review & Reviewer (Nemotron, separate job) & \code{review.md} & valid JSON with evidence for each check and a command run; approve, or two fix cycles used \\
\bottomrule\end{tabularx}
\end{table}
"""

ADRS = [
    ("001", "D1 Split", "3 builder agents + code release + separate reviewer", "one agent for everything; one per stage", "tester must not have seen the implementation; request limit forbids one long conversation", "Accepted, tested (E1)"),
    ("002", "D2 Control", "deterministic state machine, bounded back-edges", "planner agent decides what next", "reproducible, auditable, budget-bounded", "Accepted, 2 amendments"),
    ("003", "D3 Hand-offs", "short artifacts, never conversations", "pass transcripts or summaries", "limits error propagation and tokens", "Superseded in part by 011"),
    ("004", "D4 State", "files on branch \\code{autose-runs} + artifacts + PR comment", "artifacts in the PR branch; Actions cache", "PR diff stays code only; durable and linkable", "Accepted"),
    ("005", "D5 Tools", "in-process tools per role, empty command environment", "MCP servers; \\code{gh} for agents", "least privilege; small tool list", "Accepted (names changed)"),
    ("006", "D6 Models", "models chosen from laptop probes", "(see 012)", "probes did not predict the runner", "Superseded by 012"),
    ("012", "D6 Models", "one pinned model per builder role; reviewer chain; chosen after a stage ran on the runner", "cross-vendor fallback for builders", "results attributable to one model; evidence from runs", "Accepted"),
    ("007", "D7 Checks", "code gates, model call may only object", "LLM judge per stage", "reproducible decisions", "Accepted (gate bugs fixed)"),
    ("008", "D8 Reviewer", "own job, vendor, prompt, inputs, permissions + evidence rule", "same model, fresh context", "shared blind spots; rubber-stamping", "Accepted, tested (E2)"),
    ("009", "D9 Safety", "budgets, delimiters, injection classifier, keyless commands", "trust the model to ignore injections", "defence in layers, measurable", "Accepted"),
    ("010", "D10 Triggers", "label or \\code{/autose} by write access; one run per issue", "trigger on every issue", "only maintainers spend tokens", "Accepted, 1 amendment"),
    ("011", "D3 Hand-offs", "trimmed architecture note, small file reads", "full note, free-size reads", "first run exceeded the request limit", "Accepted, supersedes 003 row"),
]


def adr_table():
    out = [r"\begin{table}[ht]\centering\footnotesize",
           r"\caption{Summary of the decision records (all under \code{architecture/decisions/}).}\label{tab:adr}",
           r"\begin{tabularx}{\linewidth}{@{}l l Y Y Y l@{}}", r"\toprule",
           r"ADR & Area & Option chosen & Main option rejected & Main reason & Status \\ \midrule"]
    for a in ADRS:
        out.append(" & ".join(a) + r" \\")
    out += [r"\bottomrule\end{tabularx}", r"\end{table}"]
    return "\n".join(out)


# ---- data tables ------------------------------------------------------------------------------------------
def stage_rates():
    rs = rows("stage_pass_rates.csv")
    if not rs:
        return "No stage records yet.\n"
    out = [r"\begin{table}[ht]\centering\small",
           r"\caption{Per-stage pass rates over all recorded stage attempts (every run, including runs that later stopped).}\label{tab:rates}",
           r"\begin{tabular}{@{}l c r r r r@{}}", r"\toprule",
           r"Variant & Stage & Attempts & Passed & Rate & First-attempt rate \\ \midrule"]
    for r in rs:
        out.append("%s & %s & %s & %s & %.0f\\%% & %.0f\\%% \\\\" % (tex(r["variant"]), r["stage"], r["attempts"], r["attempts_passed"],
                   100 * float(r["attempt_pass_rate"]), 100 * float(r["first_attempt_pass_rate"])))
    out += [r"\bottomrule\end{tabular}", r"\end{table}"]
    return "\n".join(out)


def per_issue():
    rs = [r for r in rows("results.csv")]
    if not rs:
        return "No results yet.\n"
    out = [r"\begin{table}[ht]\centering\small",
           r"\caption{Result of each pipeline or variant round: hidden acceptance tests (passed/total), regressions among the 228 baseline tests, and the reviewer's verdict on that round.}\label{tab:issues}",
           r"\begin{tabular}{@{}r l c c c c r r l@{}}", r"\toprule",
           r"Issue & Variant & Round & PR & Hidden & Regr. & Tokens & Reviewer & \\ \midrule"]
    for r in rs:
        hid = "%s/%s" % (r["hidden_passed"], r["hidden_total"]) if r["hidden_total"] else tex(r["hidden_outcome"])
        out.append("\\#%s & %s & %s & %s & %s & %s & %s & %s & \\\\" % (r["issue"], tex(r["variant"]), r["round"], ("\\#" + r["pr"]) if r["pr"] else "--",
                   hid, r["regressions"] or "--", r["tokens"] or "--", tex(r["review_verdict"].replace("_", " ").lower())))
    out += [r"\bottomrule\end{tabular}", r"\end{table}"]
    return "\n".join(out)


def seeded_summary():
    rs = rows("seeded.csv")
    if not rs:
        return "No calibration reviews yet.\n"
    by = defaultdict(lambda: defaultdict(list))
    for r in rs:
        by[r["variant"] + " " + r["reviewer_version"]][(r["pr"], r["label"])].append(r["outcome"])
    out = [r"\begin{table}[ht]\centering\small",
           r"\caption{Reviewer calibration on the five seeded pull requests: outcome of every trial. A correct pull request should be approved; a wrong one should be rejected.}\label{tab:seeded}",
           r"\begin{tabular}{@{}l l l l@{}}", r"\toprule", r"Variant & PR (label) & Outcomes by trial & Right/valid \\ \midrule"]
    for variant in sorted(by):
        for (pr, label), outs in sorted(by[variant].items()):
            good = sum(o in ("caught", "approved") for o in outs)
            valid = sum(o != "no valid review" for o in outs)
            out.append("%s & \\#%s (%s) & %s & %d/%d \\\\" % (tex(variant), pr, label, tex(", ".join(outs)), good, valid))
    out += [r"\bottomrule\end{tabular}", r"\end{table}"]
    return "\n".join(out)



def e2_summary():
    rs = [r for r in rows("seeded.csv") if r["reviewer_version"] == "v3"]
    if not rs:
        return "No calibration reviews with the final reviewer yet.\n"
    by = defaultdict(list)
    for r in rs:
        by[r["variant"]].append(r)
    out = [r"\begin{table}[ht]\centering\small",
           r"\caption{E2, reviewer independence: all reviews by the final reviewer on the five seeded pull requests (three trials per pull request).}\label{tab:e2}",
           r"\begin{tabular}{@{}l r r r r r r r@{}}", r"\toprule",
           r"Variant & Reviews & Valid & Wrong PRs caught & Wrong PRs missed & Correct PRs approved & Correct PRs rejected & Mean tokens \\ \midrule"]
    for variant, xs in sorted(by.items()):
        wrong = [x for x in xs if x["label"] == "wrong"]
        corr = [x for x in xs if x["label"] == "correct"]
        valid = [x for x in xs if x["outcome"] != "no valid review"]
        toks = [int(x["tokens"]) for x in xs if x["tokens"]]
        out.append("%s & %d & %d & %d/%d & %d/%d & %d/%d & %d/%d & %s \\\\" % (
            tex(variant), len(xs), len(valid),
            sum(x["outcome"] == "caught" for x in wrong), len(wrong), sum(x["outcome"] == "missed" for x in wrong), len(wrong),
            sum(x["outcome"] == "approved" for x in corr), len(corr), sum(x["outcome"] == "false rejection" for x in corr), len(corr),
            "%d" % (sum(toks) / len(toks)) if toks else "--"))
    out += [r"\bottomrule\end{tabular}", r"\end{table}"]
    return "\n".join(out)


def e1_summary():
    rs = [r for r in rows("results.csv") if r["round"] == "1"]
    if not any(r["variant"] == "single" for r in rs):
        return "The single-agent variant has no recorded runs yet.\n"
    by = defaultdict(dict)
    for r in rs:
        by[r["issue"]][r["variant"]] = r
    out = [r"\begin{table}[ht]\centering\small",
           r"\caption{E1, splitting the work: the split pipeline and the single agent on the same issues, compared at the end of round 1 (before any review feedback).}\label{tab:e1}",
           r"\begin{tabular}{@{}r l c c c c r@{}}", r"\toprule",
           r"Issue & Variant & PR opened & Hidden tests & Regressions & First-try gates 1--4 & Tokens \\ \midrule"]
    for issue in sorted(by, key=int):
        for variant in ("pipeline", "single"):
            r = by[issue].get(variant)
            if not r:
                continue
            gates = sum(int(r["stage%d_first_try" % n] or 0) for n in (1, 2, 3, 4)) if variant == "pipeline" else "--"
            hid = "%s/%s" % (r["hidden_passed"], r["hidden_total"]) if r["hidden_total"] else tex(r["hidden_outcome"])
            out.append("\\#%s & %s & %s & %s & %s & %s & %s \\\\" % (issue, variant, "yes" if r["released"] == "yes" else "no", hid,
                       r["regressions"] or "--", gates, r["tokens"] or "--"))
    out += [r"\bottomrule\end{tabular}", r"\end{table}"]
    return "\n".join(out)


def write(name, text):
    (GEN / name).write_text(text)


def main():
    write("stage_table.tex", STAGES)
    write("adr_table.tex", adr_table())
    write("experiments.tex", e1_summary() + "\n" + e2_summary() + "\n" +
          ((R / "text" / "experiments.tex").read_text() if (R / "text" / "experiments.tex").exists() else ""))
    write("results.tex", stage_rates() + "\n" + per_issue() + "\n" + seeded_summary() + "\n" +
          ((R / "text" / "results.tex").read_text() if (R / "text" / "results.tex").exists() else ""))
    for n in ("hindsight", "limitations", "appendix"):
        p = R / "text" / (n + ".tex")
        write(n + ".tex", p.read_text() if p.exists() else "Pending.\n")
    for _ in range(2):
        p = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "report.tex"], cwd=R, capture_output=True, text=True)
        if p.returncode:
            print(p.stdout[-1500:])
            sys.exit(1)
    pages = subprocess.run(["pdfinfo", "report.pdf"], cwd=R, capture_output=True, text=True).stdout
    print([l for l in pages.splitlines() if l.startswith("Pages")])


if __name__ == "__main__":
    main()

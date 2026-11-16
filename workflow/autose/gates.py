"""Stage gates. They are code, not model opinions (ADR-007): each returns
(ok, reasons) so a failure can be fed back to the next attempt as plain facts."""
import re
import sys
import subprocess
from pathlib import Path

from . import config, llm, tools

VAGUE = re.compile(r"\b(fast|quick|easy|easily|user-friendly|robust|secure|scalable|flexible|"
                   r"intuitive|appropriate|appropriately|nice|good|better|properly|etc)\b", re.I)
MAX_WORDS = {"spec": 1000, "design": 800}


def norm(t):
    """Models sometimes write non-breaking or typographic hyphens in ids; treat them as "-"."""
    return re.sub("[\u2010-\u2015\u2212]", "-", t)


def words(t):
    return len(t.split())


# -- stage 1 ---------------------------------------------------------------
def parse_acs(spec):
    spec = norm(spec)
    acs = {}
    sec = re.search(r"##\s*Acceptance criteria(.*?)(?=\n##\s|\Z)", spec, re.S | re.I)
    if sec:
        for m in re.finditer(r"^\s*[-*]\s*AC-(\d+)\b[^:\n]*:\s*(.+)$", sec.group(1), re.M):
            acs[int(m.group(1))] = m.group(2).strip()
    return acs


def gate_spec(spec):
    spec = norm(spec)
    r = []
    for h in ("Source statements", "Requirements", "Acceptance criteria", "Assumptions"):
        if not re.search(r"^##\s*" + h, spec, re.M | re.I):
            r.append("missing section: " + h)
    acs = parse_acs(spec)
    if not acs:
        r.append("no acceptance criteria found (use lines like `- AC-1 (FR-1): Given ..., when ..., then ...`)")
    for n, t in acs.items():
        low = t.lower()
        if not (re.search(r"\bgiven\b", low) and re.search(r"\bwhen\b", low) and re.search(r"\bthen\b", low)):
            r.append("AC-%d is not in Given/When/Then form" % n)
        if "tbd" in low or "[" in t and "]" in t and "tbd" in low:
            r.append("AC-%d contains a placeholder" % n)
        m = VAGUE.search(t.split("then", 1)[-1] if "then" in low else t)
        if m:
            r.append("AC-%d uses a vague word in its outcome: '%s'" % (n, m.group(0)))
    frs = set(int(x) for x in re.findall(r"\bFR-(\d+)\b", spec))
    refs = set(int(x) for x in re.findall(r"^\s*[-*]\s*AC-\d+\s*\(FR-(\d+)", spec, re.M))
    if frs and not frs <= refs:
        r.append("requirements without an acceptance criterion: " + ", ".join("FR-%d" % x for x in sorted(frs - refs)))
    if words(spec) > MAX_WORDS["spec"]:
        r.append("spec is too long (%d words, limit %d); shorten it" % (words(spec), MAX_WORDS["spec"]))
    return not r, r


# -- stage 2 ---------------------------------------------------------------
def design_rows(design):
    design = norm(design)
    sec = re.search(r"##\s*Changes(.*?)(?=\n##\s|\Z)", design, re.S | re.I)
    rows = []
    for line in (sec.group(1) if sec else "").splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and cells[0].lower() not in ("file", "---", "") and not set(cells[0]) <= set("-: "):
            # a Change cell may itself contain "|" (e.g. type hints), so take the last cell as the ACs
            rows.append([cells[0], cells[1], " | ".join(cells[2:-1]), cells[-1]])
    return rows


def design_files(design):
    return {r[0] for r in design_rows(design)}


def gate_design(design, spec, workdir):
    r = []
    rows = design_rows(design)
    if not rows:
        r.append("no table rows under `## Changes` (columns: File | Function or class | Change | ACs)")
    wd = Path(workdir)
    covered = set()
    for f, fn, change, acs in rows:
        p = (wd / f)
        top = Path(f).parts[0] if Path(f).parts else ""
        if top in config.DENY or f.startswith("/") or ".." in f:
            r.append("`%s` is not a file you may change" % f)
            continue
        is_new = "new" in (fn + " " + change).lower()
        if not p.exists():
            if not is_new:
                r.append("file does not exist: %s (mark it NEW if you will create it)" % f)
            continue
        name = re.split(r"[.\s(,]", fn.strip())[-1] if fn.strip() else ""
        name = re.sub(r"\W", "", name)
        if name and not is_new and name.lower() not in ("none", "module", "n/a"):
            if not re.search(r"\b%s\b" % re.escape(name), p.read_text(errors="replace")):
                r.append("`%s` not found in %s (mark it NEW if it is new)" % (name, f))
        covered |= {int(x) for x in re.findall(r"AC-?(\d+)", acs)}
    need = set(parse_acs(spec))
    if need - covered:
        r.append("acceptance criteria not covered by any row: " + ", ".join("AC-%d" % n for n in sorted(need - covered)))
    if words(design) > MAX_WORDS["design"]:
        r.append("design is too long (%d words, limit %d)" % (words(design), MAX_WORDS["design"]))
    return not r, r


# -- stage 3 ---------------------------------------------------------------
def sh(args, cwd, timeout=300):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    return p.returncode, (p.stdout + p.stderr)


def changed_files(workdir, base):
    rc, out = sh(["git", "diff", "--name-only", base], workdir)
    rc2, out2 = sh(["git", "ls-files", "--others", "--exclude-standard"], workdir)
    return sorted({x for x in (out + "\n" + out2).splitlines() if x.strip()})


def gate_impl(workdir, base, design):
    r = []
    files = changed_files(workdir, base)
    if not files:
        return False, ["the diff is empty; nothing was changed"]
    allowed = design_files(design)
    for f in files:
        if f.startswith("tests/") and not f.startswith("tests/test_autose_"):
            continue            # existing tests may be updated when the design says so
        if f not in allowed:
            r.append("changed a file the design does not name: " + f)
    rc, out = sh([sys.executable, "-m", "compileall", "-q", "tinydb"], workdir)
    if rc:
        r.append("compileall failed: " + out[-300:])
    rc, out = sh([sys.executable, "-c", "import tinydb"], workdir)
    if rc:
        r.append("import tinydb failed: " + out[-300:])
    return not r, r


# -- stage 4 ---------------------------------------------------------------
def test_names(workdir):
    names = []
    for f in Path(workdir, "tests").glob("test_autose_*.py"):
        names += re.findall(r"^def (test_ac(\d+)_\w*)\(", f.read_text(), re.M)
    return names


def failing_tests(output):
    return sorted(set(re.findall(r"FAILED (\S+)", output)))


def classify_failures(out):
    """Split failing new tests into those that fail on an assertion (the behaviour is wrong,
    an implementation problem) and those that crash inside the test file itself with another
    exception type (the test is wrong, a tester problem)."""
    tester_bugs, impl = [], []
    for m in re.finditer(r"^(tests/test_autose_\w+\.py):(\d+): (\w+)", out, re.M):
        (impl if m.group(3) == "AssertionError" else tester_bugs).append("%s:%s %s" % m.groups())
    others = re.findall(r"^(?!tests/test_autose_)(\S+\.py):\d+: \w+", out, re.M)   # raised inside the library
    return tester_bugs, impl, others


def gate_tests(workdir, base, spec):
    """New tests must exist for every criterion, fail on the base code, and pass
    on the new code together with the whole existing suite."""
    r, report = [], {}
    names = test_names(workdir)
    have = {int(n) for _, n in names}
    need = set(parse_acs(spec))
    if not names:
        return False, ["no tests named test_ac<N>_... found in tests/test_autose_*.py"], report
    if need - have:
        r.append("no test for: " + ", ".join("AC-%d" % n for n in sorted(need - have)))
    # 1. new tests on the base commit must fail somewhere (otherwise they prove nothing)
    base_dir = Path(workdir).parent / "base_checkout"
    sh(["rm", "-rf", str(base_dir)], workdir)
    sh(["git", "worktree", "prune"], workdir)
    rc, out = sh(["git", "worktree", "add", "--detach", str(base_dir), base], workdir)
    if rc:
        return False, ["cannot create base checkout: " + out[-200:]], report
    try:
        for f in Path(workdir, "tests").glob("test_autose_*.py"):
            (base_dir / "tests" / f.name).write_text(f.read_text())
        files = [str(Path("tests") / f.name) for f in Path(workdir, "tests").glob("test_autose_*.py")]
        out = tools.run_isolated([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-o", "addopts="] + files, base_dir)
        report["base_failed"] = failing_tests(out)
        if not report["base_failed"] and "error" not in out.lower():
            r.append("every new test already passes on the base commit, so they do not test the change")
    finally:
        sh(["git", "worktree", "remove", "--force", str(base_dir)], workdir)
    # 2. everything on the new code
    out = tools.run_isolated([sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q", "-o", "addopts=", "tests"], workdir, timeout=280)
    report["suite_output"] = out
    report["failed"] = failing_tests(out)
    report["tester_bugs"], report["impl_failures"], report["library_errors"] = classify_failures(out)
    if not out.startswith("exit code 0"):
        r.append("test suite does not pass: " + ", ".join(report["failed"][:8] or ["see output"]))
    m = re.search(r"(\d+) passed", out)
    report["passed"] = int(m.group(1)) if m else 0
    return not r, r, report


# -- stage 6 ---------------------------------------------------------------
def gate_review(js, ran_command):
    r = []
    if not isinstance(js, dict):
        return False, ["reviewer did not return a JSON object"]
    v = js.get("verdict")
    if v not in ("APPROVE", "REQUEST_CHANGES"):
        r.append("verdict must be APPROVE or REQUEST_CHANGES")
    checks = js.get("checks") or []
    good = [c for c in checks if isinstance(c, dict) and str(c.get("evidence", "")).strip()]
    if len(good) < 2:
        r.append("fewer than two checks with evidence")
    if not ran_command:
        r.append("the reviewer never ran a command; claims are unproven")
    if v == "APPROVE" and any(f.get("severity") in ("high", "medium") for f in js.get("findings") or [] if isinstance(f, dict)):
        r.append("APPROVE with medium or high findings")
    if v == "REQUEST_CHANGES":
        if js.get("issue_class") not in ("approach", "code"):
            r.append("REQUEST_CHANGES needs issue_class approach or code")
        if not [f for f in js.get("findings") or [] if isinstance(f, dict) and f.get("text")]:
            r.append("REQUEST_CHANGES needs at least one finding")
    return not r, r

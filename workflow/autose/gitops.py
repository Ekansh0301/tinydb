"""Git and GitHub helpers. Authentication uses a per-command header so the token
never appears in a remote URL or in a log (ADR-009)."""
import base64
import json
import os
import re
import subprocess
import time
from pathlib import Path

from . import config


SECRET_PATTERNS = [
    (re.compile(r"(AUTHORIZATION:\s*basic\s+)[A-Za-z0-9+/=_-]+", re.I), r"\1<redacted>"),
    (re.compile(r"x-access-token:[^@\s'\"]+"), "x-access-token:<redacted>"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}"), "<redacted-token>"),
    (re.compile(r"\bgsk_[A-Za-z0-9]{20,}"), "<redacted-key>"),
    (re.compile(r"\bnvapi-[A-Za-z0-9_-]{20,}"), "<redacted-key>"),
]


def redact(text):
    """Remove anything that looks like a credential from text that may be logged, commented or stored."""
    for rx, repl in SECRET_PATTERNS:
        text = rx.sub(repl, text or "")
    return text


def safe_cmd(args):
    """The command without its `-c key=value` options, which can carry the authorization header."""
    out, skip = [], False
    for a in args:
        if skip:
            skip = False
            continue
        if a == "-c":
            skip = True
            continue
        out.append(a)
    return " ".join(out[:3])


def run(args, cwd=None, check=True, env=None, input=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, env=env, input=input)
    if check and p.returncode:
        raise RuntimeError(redact("%s failed: %s" % (safe_cmd(args), (p.stderr or p.stdout)[-400:])))
    return p.stdout.strip()


def auth_args():
    tok = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not tok:
        return []
    b = base64.b64encode(("x-access-token:" + tok).encode()).decode()
    return ["-c", "http.https://github.com/.extraheader=AUTHORIZATION: basic " + b]


def git(args, cwd, check=True):
    return run(["git"] + auth_args() + args, cwd=cwd, check=check)


def git_ok(args, cwd):
    """Run a git command and report only whether it succeeded."""
    return subprocess.run(["git"] + auth_args() + args, cwd=cwd, capture_output=True, text=True).returncode == 0


def gh(args, check=True, input=None):
    return run(["gh"] + args, check=check, input=input)


def gh_json(args):
    return json.loads(gh(args) or "null")


def repo_url():
    return "https://github.com/%s.git" % config.REPO


def assert_our_repo():
    """The workflow may act only on this repository (task rule: never upstream)."""
    got = os.environ.get("GITHUB_REPOSITORY")
    if got and got != config.REPO:
        raise SystemExit("refusing to run in %s; only %s is allowed" % (got, config.REPO))


class Runs:
    """Durable state on the autose-runs branch (ADR-004): artifacts and state.json."""

    def __init__(self, root, issue, round_no):
        self.root = Path(root)
        self.issue = issue
        self.round = round_no
        self.dir = self.root / "runs" / ("issue-%s" % issue) / ("round-%s" % round_no)

    def open(self, remote=True):
        if (self.root / ".git").exists():
            return
        self.root.mkdir(parents=True, exist_ok=True)
        git(["init", "-q", "-b", config.RUNS_BRANCH], self.root)
        git(["config", "user.name", "autose-bot"], self.root)
        git(["config", "user.email", "autose-bot@users.noreply.github.com"], self.root)
        if remote:
            git(["remote", "add", "origin", repo_url()], self.root)
            got = git(["ls-remote", "--heads", "origin", config.RUNS_BRANCH], self.root, check=False)
            if got:
                git(["fetch", "-q", "origin", config.RUNS_BRANCH], self.root)
                git(["reset", "-q", "--hard", "FETCH_HEAD"], self.root)

    def write(self, name, text):
        self.dir.mkdir(parents=True, exist_ok=True)
        (self.dir / name).write_text(text)

    def append(self, name, text):
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / name, "a") as f:
            f.write(text)

    def read(self, name, default=None):
        f = self.dir / name
        return f.read_text() if f.exists() else default

    def state(self):
        f = self.root / "runs" / ("issue-%s" % self.issue) / "state.json"
        return json.loads(f.read_text()) if f.exists() else {}

    def save_state(self, st):
        f = self.root / "runs" / ("issue-%s" % self.issue) / "state.json"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(st, indent=2, sort_keys=True))

    def persist(self, message, remote=True):
        git(["add", "-A"], self.root)
        if not git(["status", "--porcelain"], self.root):
            return
        git(["commit", "-q", "-m", message], self.root)
        if not remote:
            return
        for i in range(4):
            if git_ok(["push", "-q", "origin", "HEAD:" + config.RUNS_BRANCH], self.root):
                return
            git_ok(["pull", "-q", "--rebase", "origin", config.RUNS_BRANCH], self.root)
            time.sleep(2)
        raise RuntimeError("could not push the runs branch")

"""Tools an agent can call. Every role gets a different subset (ADR-005), all
paths are confined to the work directory, and commands run with an empty
environment so no API key is ever visible to code an agent executes."""
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from . import config

TEXT_EXT = {".py", ".md", ".txt", ".rst", ".toml", ".ini", ".cfg", ".yaml", ".yml", ".json", ""}

SPECS = {
    "open_file": ("Open a text file and show numbered lines (at most 80 lines per call).",
                  {"path": "string", "line_start": "integer", "line_end": "integer"}, ["path"]),
    "list_dir": ("List a directory.", {"path": "string"}, []),
    "search": ("Search files for a regular expression. Returns file:line:text.",
             {"pattern": "string", "path": "string"}, ["pattern"]),
    "edit_file": ("Replace one exact, unique occurrence of `old` with `new` in a file.",
                  {"path": "string", "old": "string", "new": "string"}, ["path", "old", "new"]),
    "write_file": ("Create a new file or overwrite a file you created.",
                   {"path": "string", "content": "string"}, ["path", "content"]),
    "run": ("Run `python -m pytest ...`, `python -m compileall ...` or `python -c ...` in the repository.",
            {"command": "string"}, ["command"]),
}
ROLE_TOOLS = {
    "planner": ["open_file", "list_dir", "search"],
    "implementer": ["open_file", "list_dir", "search", "edit_file", "write_file", "run"],
    "tester": ["open_file", "list_dir", "search", "write_file", "edit_file", "run"],
    "reviewer": ["open_file", "list_dir", "search", "run"],
    "single": ["open_file", "list_dir", "search", "edit_file", "write_file", "run"],
}


def schemas(role):
    out = []
    for name in ROLE_TOOLS[role]:
        desc, props, req = SPECS[name]
        out.append({"type": "function", "function": {
            "name": name, "description": desc,
            "parameters": {"type": "object",
                           "properties": {k: {"type": v} for k, v in props.items()},
                           "required": req}}})
    return out


class ToolError(Exception):
    pass


class Toolbox:
    def __init__(self, workdir, role):
        self.root = Path(workdir).resolve()
        self.role = role
        self.calls = []          # (name, args) history, used by gates and loop detection
        self.ran_command = False
        self.edits = 0           # successful edit_file / write_file calls

    # -- path policy --------------------------------------------------------
    def _path(self, p, write=False):
        p = (p or ".").strip()
        full = (self.root / p).resolve()
        try:
            rel = full.relative_to(self.root)
        except ValueError:
            raise ToolError("path is outside the repository")
        if rel.parts and rel.parts[0] in config.DENY:
            raise ToolError("path is not available")
        if write:
            s = rel.as_posix()
            if self.role == "tester" and not re.fullmatch(r"tests/test_autose_[A-Za-z0-9_]+\.py", s):
                raise ToolError("the tester may only write tests/test_autose_<name>.py")
            if self.role == "implementer" and re.fullmatch(r"tests/test_autose_.*", s):
                raise ToolError("test_autose_* files belong to the tester")
            if self.role in ("planner", "reviewer"):
                raise ToolError("this role cannot write")
            if self.role == "single" and s.startswith("tests/") and not re.fullmatch(r"tests/test_autose_[A-Za-z0-9_]+\.py", s):
                raise ToolError("write new tests only as tests/test_autose_<name>.py")
        return full

    def _cap(self, s):
        n = config.BUDGET["tool_chars"]
        return s if len(s) <= n else s[:n] + "\n[output truncated]"

    # -- tools --------------------------------------------------------------
    ALIASES = {"start_line": "line_start", "start": "line_start", "from_line": "line_start",
               "end_line": "line_end", "end": "line_end", "to_line": "line_end",
               "file": "path", "filepath": "path", "file_path": "path", "filename": "path",
               "regex": "pattern", "query": "pattern", "cmd": "command",
               "old_string": "old", "new_string": "new", "text": "content"}

    def call(self, name, args):
        name = {"read_file": "open_file", "grep": "search"}.get(name, name)
        args = {self.ALIASES.get(k, k): v for k, v in args.items()}
        self.calls.append((name, repr(sorted(args.items()))))
        if name not in ROLE_TOOLS[self.role]:
            return "error: tool not available to this role"
        try:
            return self._cap(getattr(self, "t_" + name)(**args))
        except ToolError as e:
            return "error: %s" % e
        except TypeError:
            valid = ", ".join(SPECS[name][1])
            return "error: bad arguments; valid arguments for %s are: %s" % (name, valid)

    def t_open_file(self, path, line_start=1, line_end=None):
        f = self._path(path)
        if not f.is_file():
            raise ToolError("no such file")
        lines = f.read_text(errors="replace").splitlines()
        a = max(int(line_start or 1), 1)
        b = min(int(line_end or a + 59), a + 79, len(lines))
        body = "\n".join("%d: %s" % (i, lines[i - 1]) for i in range(a, b + 1))
        return "%s (lines %d-%d of %d)\n%s" % (path, a, b, len(lines), body)

    def t_list_dir(self, path="."):
        d = self._path(path)
        if not d.is_dir():
            raise ToolError("not a directory")
        names = sorted(p.name + ("/" if p.is_dir() else "") for p in d.iterdir()
                       if not (d == self.root and p.name in config.DENY) and not p.name.startswith("__pycache__"))
        return "\n".join(names) or "(empty)"

    def t_search(self, pattern, path="."):
        base = self._path(path)
        try:
            rx = re.compile(pattern)
        except re.error as e:
            raise ToolError("bad regex: %s" % e)
        files = [base] if base.is_file() else sorted(base.rglob("*"))
        out = []
        for f in files:
            rel = f.relative_to(self.root)
            if (rel.parts and rel.parts[0] in config.DENY) or "__pycache__" in rel.parts \
                    or not f.is_file() or f.suffix not in TEXT_EXT:
                continue
            for i, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                if rx.search(line):
                    out.append("%s:%d:%s" % (rel.as_posix(), i, line.strip()[:160]))
                    if len(out) >= 40:
                        return "\n".join(out) + "\n[more matches omitted]"
        return "\n".join(out) or "no matches"

    def t_edit_file(self, path, old, new):
        f = self._path(path, write=True)
        if not f.is_file():
            raise ToolError("no such file (use write_file to create one)")
        text = f.read_text()
        if old == "":
            raise ToolError("`old` must not be empty")
        n = text.count(old)
        if n != 1:
            raise ToolError("`old` must match exactly once, it matches %d times" % n)
        f.write_text(text.replace(old, new))
        self.edits += 1
        return "edited %s" % path

    def t_write_file(self, path, content):
        f = self._path(path, write=True)
        if f.exists() and self.role in ("implementer", "single") and not f.name.startswith("test_autose_"):
            raise ToolError("file exists, use edit_file")
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
        self.edits += 1
        return "wrote %s (%d bytes)" % (path, len(content))

    def t_run(self, command):
        try:
            argv = shlex.split(command)
        except ValueError as e:
            raise ToolError("cannot parse command: %s" % e)
        ok = (argv[:2] == ["python", "-m"] and len(argv) > 2 and argv[2] in ("pytest", "compileall")) \
            or (argv[:2] == ["python", "-c"] and len(argv) == 3)
        if not ok:
            raise ToolError("only `python -m pytest`, `python -m compileall` and `python -c` are allowed")
        argv[0] = sys.executable
        if argv[1] == "-m" and argv[2] == "pytest":
            argv += ["-p", "no:cacheprovider", "-q", "-o", "addopts="]
        self.ran_command = True
        return run_isolated(argv, self.root)


_BWRAP = {}


def _bwrap_ok():
    if "ok" not in _BWRAP:
        _BWRAP["ok"] = False
        if shutil.which("bwrap") and os.environ.get("AUTOSE_BWRAP", "1") == "1":
            try:
                _BWRAP["ok"] = subprocess.run(["bwrap", "--ro-bind", "/", "/", "true"],
                                              capture_output=True, timeout=10).returncode == 0
            except Exception:
                pass
    return _BWRAP["ok"]


def run_isolated(argv, cwd, timeout=None):
    """Run a command with an empty environment (and bubblewrap when available)."""
    home = tempfile.mkdtemp(prefix="autose-home-")
    env = {"PATH": "/usr/bin:/bin", "HOME": home, "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONPATH": str(cwd), "LANG": "C.UTF-8", "TMPDIR": home}
    cmd = list(argv)
    if _bwrap_ok():
        cmd = ["bwrap", "--ro-bind", "/", "/", "--dev", "/dev", "--proc", "/proc",
               "--tmpfs", "/home", "--tmpfs", "/root", "--bind", str(cwd), str(cwd),
               "--bind", home, home, "--unshare-net", "--chdir", str(cwd)] + cmd
    try:
        r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True,
                           timeout=timeout or config.BUDGET["run_timeout"])
        out = (r.stdout + r.stderr)
        return "exit code %d\n%s" % (r.returncode, out[-3000:])
    except subprocess.TimeoutExpired:
        return "error: command timed out"
    finally:
        shutil.rmtree(home, ignore_errors=True)

import os
import sys

import pytest

from autose import config, tools


def box(tmp_path, role):
    (tmp_path / "tinydb").mkdir(exist_ok=True)
    (tmp_path / "tinydb" / "a.py").write_text("def f():\n    return 1\n")
    (tmp_path / "experiment").mkdir(exist_ok=True)
    (tmp_path / "experiment" / "secret.txt").write_text("hidden tests live here")
    return tools.Toolbox(tmp_path, role)


def test_cannot_read_outside_or_denied_paths(tmp_path):
    tb = box(tmp_path, "planner")
    assert "outside" in tb.call("open_file", {"path": "../x"})
    assert "not available" in tb.call("open_file", {"path": "experiment/secret.txt"})
    assert "hidden tests" not in tb.call("search", {"pattern": "hidden"})
    assert "experiment" not in tb.call("list_dir", {"path": "."})


def test_roles_have_different_tools(tmp_path):
    assert "not available" in box(tmp_path, "planner").call("edit_file", {"path": "tinydb/a.py", "old": "1", "new": "2"})
    assert "not available" in box(tmp_path, "reviewer").call("write_file", {"path": "x.py", "content": ""})
    assert "open_file" not in tools.ROLE_TOOLS["nobody"] if "nobody" in tools.ROLE_TOOLS else True


def test_tester_can_only_write_its_own_test_file(tmp_path):
    tb = box(tmp_path, "tester")
    assert "error" in tb.call("write_file", {"path": "tinydb/a.py", "content": "x"})
    assert tb.call("write_file", {"path": "tests/test_autose_x.py", "content": "def test_ac1_a(): pass\n"}).startswith("wrote")


def test_implementer_cannot_touch_tester_files_or_overwrite(tmp_path):
    tb = box(tmp_path, "implementer")
    assert "belong to the tester" in tb.call("write_file", {"path": "tests/test_autose_x.py", "content": ""})
    assert "file exists" in tb.call("write_file", {"path": "tinydb/a.py", "content": ""})
    assert tb.call("edit_file", {"path": "tinydb/a.py", "old": "return 1", "new": "return 2"}) == "edited tinydb/a.py"
    assert "exactly once" in tb.call("edit_file", {"path": "tinydb/a.py", "old": "zzz", "new": "y"})


def test_run_allowlist(tmp_path):
    tb = box(tmp_path, "implementer")
    assert "only" in tb.call("run", {"command": "rm -rf /"})
    assert "only" in tb.call("run", {"command": "python script.py"})
    assert tb.call("run", {"command": "python -c 'print(41+1)'"}).endswith("42\n")


def test_commands_never_see_api_keys(tmp_path, monkeypatch):
    monkeypatch.setenv("GROQ_API_KEYS", "gsk_secretvalue")
    monkeypatch.setenv("GH_TOKEN", "ghs_secretvalue")
    tb = box(tmp_path, "reviewer")
    out = tb.call("run", {"command": "python -c 'import os; print(sorted(os.environ))'"})
    assert "secretvalue" not in out and "GROQ" not in out and "GH_TOKEN" not in out


def test_argument_aliases_and_tool_name_aliases(tmp_path):
    tb = box(tmp_path, "planner")
    out = tb.call("read_file", {"file": "tinydb/a.py", "start_line": 1, "end_line": 1})
    assert "def f" in out


def test_agent_is_reminded_once_when_it_finishes_without_editing(tmp_path):
    from autose import agent

    class Fake:
        served = []

        def __init__(self):
            self.n = 0

        def chat(self, messages, tools=None, max_tokens=None, temperature=0.2):
            self.n += 1
            if self.n == 1:
                return {"role": "assistant", "content": "I changed it."}, 10, "fake"
            if self.n == 2:
                return {"role": "assistant", "content": "", "tool_calls": [
                    {"id": "1", "function": {"name": "edit_file", "arguments":
                     '{"path": "tinydb/a.py", "old": "return 1", "new": "return 2"}'}}]}, 10, "fake"
            return {"role": "assistant", "content": "done"}, 10, "fake"

    tb = box(tmp_path, "implementer")
    res = agent.run_agent("implementer", Fake(), "sys", "user", tb, must_edit=True)
    assert res.text == "done" and tb.edits == 1 and res.reminded


def test_tester_can_extend_its_own_file_but_not_edit_the_library(tmp_path):
    tb = box(tmp_path, "tester")
    tb.call("write_file", {"path": "tests/test_autose_x.py", "content": "def test_ac1_a():\n    pass\n"})
    assert tb.call("edit_file", {"path": "tests/test_autose_x.py", "old": "pass", "new": "assert True"}) == "edited tests/test_autose_x.py"
    assert "error" in tb.call("edit_file", {"path": "tinydb/a.py", "old": "return 1", "new": "return 2"})


def test_write_file_reports_what_the_python_file_contains_and_cut_off_files(tmp_path):
    tb = box(tmp_path, "tester")
    ok = tb.call("write_file", {"path": "tests/test_autose_a.py", "content": "def test_ac1_a():\n    pass\n\ndef test_ac2_b():\n    pass\n"})
    assert "defines 2 tests: test_ac1_a, test_ac2_b" in ok
    cut = tb.call("write_file", {"path": "tests/test_autose_b.py", "content": "def test_ac1_a():\n    x = (1,\n"})
    assert "syntax error" in cut and "cut off" in cut


def test_agent_is_told_once_to_wrap_up_when_most_of_the_budget_is_used(tmp_path):
    from autose import agent

    seen = []

    class Fake:
        served = []

        def chat(self, messages, tools=None, max_tokens=None, temperature=0.2):
            seen.append(messages[-1]["content"] if messages[-1]["role"] == "user" else "")
            if len(seen) < 4:
                return {"role": "assistant", "content": "", "tool_calls": [
                    {"id": str(len(seen)), "function": {"name": "list_dir", "arguments": '{"path": "%s"}' % ("." if len(seen) % 2 else "tinydb")}}]}, 10, "fake"
            return {"role": "assistant", "content": "final"}, 10, "fake"

    tb = box(tmp_path, "reviewer")
    res = agent.run_agent("reviewer", Fake(), "sys", "user", tb, stage_calls=5, wrap_up_at=0.6)
    assert res.text == "final" and res.wrapped
    assert sum("Give your final answer now" in s for s in seen) == 1

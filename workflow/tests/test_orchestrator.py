"""The state machine, with stage functions replaced by scripted outcomes."""
import pytest

from autose import orchestrator, stages
from autose.state import Ctx


class FakeRuns:
    def __init__(self):
        self.files, self._state = {}, {}

    def write(self, n, t):
        self.files[n] = t

    def append(self, n, t):
        self.files[n] = self.files.get(n, "") + t

    def read(self, n, default=None):
        return self.files.get(n, default)

    def state(self):
        return dict(self._state)

    def save_state(self, st):
        self._state = st

    def persist(self, *a, **k):
        pass


def make_ctx():
    # a path that does not exist: a test must never run git commands in a real repository
    c = Ctx(issue_no=1, issue_title="t", issue_text="b", round_no=1, workdir="/nonexistent-autose-workdir", base_sha="abc",
            branch="autose/issue-1", runs=FakeRuns(), local=True)
    return c


@pytest.fixture
def script(monkeypatch):
    calls = []

    def install(**seq):
        for name, outs in seq.items():
            it = iter(outs)

            def fn(ctx, notes=None, _n=name, _it=it):
                calls.append(_n)
                return next(_it)
            monkeypatch.setattr(stages, _name(name), fn)
        monkeypatch.setattr(stages, "stage5", lambda ctx: stages.Outcome(True, [], data={"pr": 7, "sha": "s"}))
        monkeypatch.setattr(orchestrator, "commit_code", lambda ctx, m: None)
        monkeypatch.setattr(orchestrator.gitops, "run", lambda *a, **k: "")
        return calls
    return install


def _name(n):
    return {"s1": "stage1", "s2": "stage2", "s3": "stage3", "s4": "stage4"}[n]


OK = stages.Outcome(True)


def bad(reason="x", route=""):
    return stages.Outcome(False, [reason], route=route)


def test_happy_path_runs_every_stage_once(script):
    calls = script(s1=[OK], s2=[OK], s3=[OK], s4=[OK])
    ctx = make_ctx()
    res = orchestrator.build(ctx, 1)
    assert res["status"] == "RELEASED" and calls == ["s1", "s2", "s3", "s4"]
    lines = ctx.runs.read("stages.jsonl").strip().splitlines()
    assert [__import__("json").loads(x)["stage"] for x in lines] == [1, 2, 3, 4]


def test_stage1_gets_two_retries_then_stops_and_explains_in_artifact(script):
    ctx = make_ctx()
    script(s1=[bad("no AC"), bad("no AC"), bad("no AC")])
    res = orchestrator.build(ctx, 1)
    assert res["status"] == "STOPPED" and res["stage"] == "1"
    assert "no AC" in ctx.runs.read("spec.md")


def test_failing_tests_go_back_to_implementation_at_most_twice(script):
    fail = stages.Outcome(False, ["suite"], route="impl", data={"failed": ["tests/test_autose_x.py::test_ac1_a"]})
    calls = script(s1=[OK, OK], s2=[OK, OK], s3=[OK, OK, OK], s4=[fail, fail, OK])
    # the same criterion failing twice sends the run back to the requirements once
    res = orchestrator.build(make_ctx(), 1)
    assert calls == ["s1", "s2", "s3", "s4", "s3", "s4", "s1", "s2", "s3", "s4"]
    assert res["status"] == "RELEASED"


def test_different_failures_retry_implementation_then_stop(script):
    def f(n):
        return stages.Outcome(False, ["suite"], route="impl", data={"failed": ["t::test_ac%d_x" % n]})
    calls = script(s1=[OK], s2=[OK], s3=[OK, OK, OK], s4=[f(1), f(2), f(3)])
    res = orchestrator.build(make_ctx(), 1)
    assert res["status"] == "STOPPED" and res["stage"] == "4"
    assert calls.count("s3") == 3


def test_invalid_tests_are_retried_in_the_tester_stage_only(script):
    calls = script(s1=[OK], s2=[OK], s3=[OK], s4=[bad("no test for AC-2", route="tests"), OK])
    res = orchestrator.build(make_ctx(), 1)
    assert res["status"] == "RELEASED" and calls.count("s3") == 1 and calls.count("s4") == 2


def test_starting_at_stage_three_skips_planning(script):
    calls = script(s3=[OK], s4=[OK])
    res = orchestrator.build(make_ctx(), 3)
    assert res["status"] == "RELEASED" and calls == ["s3", "s4"]


def test_single_agent_output_is_split_into_spec_and_design():
    text = "=== SPEC ===\n# Spec\nS\n=== DESIGN ===\n# Design\nD\n=== END ==="
    assert stages.split_sections(text) == ("# Spec\nS", "# Design\nD")
    assert stages.split_sections("no sections") == ("", "")


def test_single_variant_stops_after_three_attempts(monkeypatch):
    calls = []
    monkeypatch.setattr(orchestrator.gitops, "run", lambda *a, **k: "")
    monkeypatch.setattr(stages, "stage_single", lambda ctx, notes: (calls.append(1), stages.Outcome(False, ["[stage 1] x"], data={"gates": [False] * 4}))[1])
    ctx = make_ctx()
    res = orchestrator.build_single(ctx)
    assert res["status"] == "STOPPED" and len(calls) == 3


def test_an_exhausted_run_budget_stops_the_run_at_once(script):
    calls = script(s1=[OK], s2=[OK], s3=[OK], s4=[stages.Outcome(False, ["run token budget (400000) exhausted"], route="tests")])
    res = orchestrator.build(make_ctx(), 1)
    assert res["status"] == "STOPPED" and res["stage"] == "4" and calls.count("s4") == 1


def test_a_crashing_stage_ends_the_run_with_a_recorded_reason(script, monkeypatch):
    script(s1=[OK])
    def boom(ctx, notes):
        raise IsADirectoryError("tests")
    monkeypatch.setattr(stages, "stage2", boom)
    ctx = make_ctx()
    res = orchestrator.build(ctx, 1)
    assert res["status"] == "STOPPED" and "internal error" in res["reason"] and "IsADirectoryError" in res["reason"]

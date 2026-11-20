from autose import cli


def test_only_the_workflows_own_token_is_trusted_for_dispatch():
    assert cli.trusted_dispatch("workflow_dispatch", "github-actions[bot]")
    assert not cli.trusted_dispatch("issues", "github-actions[bot]")
    assert not cli.trusted_dispatch("issue_comment", "github-actions[bot]")
    assert not cli.trusted_dispatch("workflow_dispatch", "some-user")


def test_an_invalid_review_is_retried_once_on_the_next_tier(monkeypatch, tmp_path):
    from autose import review

    calls = []

    def fake_one(c, tb, user):
        calls.append(c.tiers[0][1])
        if len(calls) == 1:
            return None, ["reviewer stopped: token budget exhausted"], None
        c.served.append("x")
        return {"verdict": "APPROVE"}, [], None

    monkeypatch.setattr(review, "one_review", fake_one)
    monkeypatch.setattr(review.gitops, "run", lambda *a, **k: "")
    js, why, c, res = review.run_review(str(tmp_path), "base", "t", "b", log=lambda *_: None)
    assert js == {"verdict": "APPROVE"} and why == []
    assert calls == ["nvidia/nemotron-3-ultra-550b-a55b", "nvidia/nemotron-3.5-super-vl-120b-a12b"]
    assert [a["ok"] for a in c.attempts] == [False, True]


def test_two_invalid_reviews_mean_no_review(monkeypatch, tmp_path):
    from autose import review
    monkeypatch.setattr(review, "one_review", lambda c, tb, user: (None, ["no JSON"], None))
    monkeypatch.setattr(review.gitops, "run", lambda *a, **k: "")
    js, why, c, res = review.run_review(str(tmp_path), "base", "t", "b", log=lambda *_: None)
    assert js is None and why == ["no JSON"] and len(c.attempts) == 2


def test_the_injection_screen_fails_closed(monkeypatch):
    from autose import llm

    class Down:
        def __init__(self, role, log=print):
            pass

        def chat(self, *a, **k):
            raise llm.LLMError("down")

    monkeypatch.setattr(cli.llm, "Client", Down)
    assert cli.injection_score("any text") is None


def test_the_injection_screen_returns_the_highest_chunk_score(monkeypatch):
    class Fake:
        def __init__(self, role, log=print):
            self.scores = iter(["0.01", "0.97", "0.02"])

        def chat(self, *a, **k):
            return {"content": next(self.scores)}, 1, "fake"

    monkeypatch.setattr(cli.llm, "Client", Fake)
    assert cli.injection_score("x" * 3000) == 0.97


def test_error_messages_never_carry_the_authorization_header():
    import pytest
    from autose import gitops
    token = "ghs_" + "A" * 36
    header = "AUTHORIZATION: basic eC1hY2Nlc3MtdG9rZW46" + "Z2hzX0FBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFB"
    with pytest.raises(RuntimeError) as e:
        gitops.run(["git", "-c", "http.https://github.com/.extraheader=" + header, "no-such-subcommand"], cwd=".")
    assert "eC1hY2Nlc3Mt" not in str(e.value) and "extraheader" not in str(e.value)
    assert "<redacted>" in gitops.redact("x " + header) and token not in gitops.redact("tok " + token)
    assert "gsk_" not in gitops.redact("gsk_" + "b" * 30) and "nvapi-" not in gitops.redact("nvapi-" + "c" * 30)


def test_the_next_round_keeps_the_variant(monkeypatch):
    seen = []
    monkeypatch.setattr(cli.gitops, "gh", lambda args, **k: seen.append(args) or "")
    monkeypatch.setenv("VARIANT", "trial2")
    cli.dispatch(5, 2, 3)
    assert "variant=trial2" in seen[0] and "round=2" in seen[0] and "from_stage=3" in seen[0]

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
    assert calls == ["nvidia/nemotron-3.5-super-vl-120b-a12b", "nvidia/nemotron-3-ultra-550b-a55b"]
    assert [a["ok"] for a in c.attempts] == [False, True]


def test_two_invalid_reviews_mean_no_review(monkeypatch, tmp_path):
    from autose import review
    monkeypatch.setattr(review, "one_review", lambda c, tb, user: (None, ["no JSON"], None))
    monkeypatch.setattr(review.gitops, "run", lambda *a, **k: "")
    js, why, c, res = review.run_review(str(tmp_path), "base", "t", "b", log=lambda *_: None)
    assert js is None and why == ["no JSON"] and len(c.attempts) == 2

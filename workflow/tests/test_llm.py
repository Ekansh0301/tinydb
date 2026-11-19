import json
import urllib.error

import pytest

from autose import config, llm


class Resp:
    def __init__(self, body):
        self.body = body

    def read(self):
        return json.dumps(self.body).encode()


def http_error(code, text="", headers=None):
    import io
    return urllib.error.HTTPError("u", code, "m", headers or {}, io.BytesIO(text.encode()))


OK = {"choices": [{"message": {"role": "assistant", "content": "hi"}}], "usage": {"total_tokens": 10}}


@pytest.fixture(autouse=True)
def fresh(monkeypatch):
    for k in llm._SHARED:
        llm._SHARED[k].clear()
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setenv("GROQ_API_KEYS", "k1,k2,k3")
    monkeypatch.setenv("NVIDIA_API_KEY", "n1")


def client(monkeypatch, behaviour, role="planner"):
    c = llm.Client(role, log=lambda *_: None)
    seen = []

    def post(provider, model, key, body):
        seen.append((provider, model, key))
        r = behaviour(provider, model, key, len(seen))
        if isinstance(r, Exception):
            raise r
        return r
    monkeypatch.setattr(c, "_post", post)
    return c, seen


def test_dead_key_is_skipped_and_never_retried(monkeypatch):
    def b(p, m, k, n):
        return http_error(401) if k == "k1" else OK
    c, seen = client(monkeypatch, b)
    c.rr["groq"] = 0
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert msg["content"] == "hi"
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert [s[2] for s in seen].count("k1") == 1


def test_rate_limited_key_rotates_to_the_next(monkeypatch):
    def b(p, m, k, n):
        return http_error(429, "tpm", {"retry-after": "30"}) if k == "k1" else OK
    c, seen = client(monkeypatch, b)
    c.rr["groq"] = 0
    c.chat([{"role": "user", "content": "x"}])
    assert [s[2] for s in seen][:2] == ["k1", "k2"]


def test_oversized_prompt_leaves_no_room_and_raises(monkeypatch):
    monkeypatch.setenv("AUTOSE_TIERS_PLANNER", "groq:openai/gpt-oss-120b")
    c, seen = client(monkeypatch, lambda *a: OK)
    with pytest.raises(llm.TooLarge):
        c.chat([{"role": "user", "content": "x" * 30000}])
    assert seen == []


def test_reviewer_falls_back_through_tiers_in_order(monkeypatch):
    def b(p, m, k, n):
        return http_error(503, "busy") if p == "nvidia" else OK
    c, seen = client(monkeypatch, b, role="reviewer")
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert label == "groq:qwen/qwen3.8-27b"
    models = [s[1] for s in seen]
    assert models.index("nvidia/nemotron-3-ultra-550b-a55b") < models.index("nvidia/nemotron-3.5-super-vl-120b-a12b")


def test_all_tiers_failing_raises_never_returns_text(monkeypatch):
    c, seen = client(monkeypatch, lambda *a: http_error(503, "busy"), role="reviewer")
    with pytest.raises(llm.LLMError):
        c.chat([{"role": "user", "content": "x"}])


def test_builder_is_pinned_to_one_model_by_default():
    assert [t[1] for r in ("planner", "implementer") for t in llm.config.tiers(r)] == ["openai/gpt-oss-120b"] * 2
    assert llm.config.tiers("tester")[0][1] != llm.config.tiers("implementer")[0][1]


def test_builder_falls_back_to_the_second_vendor_when_the_daily_quota_is_used_up(monkeypatch):
    monkeypatch.setenv("AUTOSE_TIERS_PLANNER", "groq:openai/gpt-oss-120b,nvidia:poolside/laguna-xs-2.1")
    def b(p, m, k, n):
        if p == "groq":
            return http_error(429, "Rate limit reached on tokens per day (TPD): Limit 200000, Used 199000")
        return OK
    c, seen = client(monkeypatch, b)
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert label == "nvidia:poolside/laguna-xs-2.1"
    assert all(c.cooldown[("groq", i)] > llm.time.time() + 800 for i in range(3))   # daily quota: long cooldown


def test_malformed_tool_call_is_reported_not_fatal(monkeypatch):
    c, seen = client(monkeypatch, lambda *a: http_error(400, '{"code":"tool_use_failed"}'))
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert msg.get("_malformed_tool_call")


def test_a_tier_whose_keys_are_all_set_aside_is_skipped_at_once(monkeypatch):
    monkeypatch.setenv("AUTOSE_TIERS_PLANNER", "groq:openai/gpt-oss-120b,nvidia:poolside/laguna-xs-2.1")
    seen_waits = []
    monkeypatch.setattr(llm.time, "sleep", lambda s: seen_waits.append(s))

    def b(p, m, k, n):
        return OK if p == "nvidia" else http_error(500)
    c, seen = client(monkeypatch, b)
    for i in range(3):
        c.cooldown[("groq", i)] = llm.time.time() + 1000      # e.g. daily quota used up
    msg, used, label = c.chat([{"role": "user", "content": "x"}])
    assert label.startswith("nvidia:")
    assert seen_waits == []                                    # it did not wait for the Groq keys
    assert all(s[0] == "nvidia" for s in seen)


def test_an_endpoint_that_never_answers_is_given_up_after_four_timeouts(monkeypatch):
    c, seen = client(monkeypatch, lambda *a: TimeoutError("hang"))
    with pytest.raises(llm.LLMError):
        c.chat([{"role": "user", "content": "x"}])
    assert len(seen) == 4

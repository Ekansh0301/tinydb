"""Chat client for OpenAI-compatible endpoints: key rotation, per-key token
window, retries, and model tiers with fallback (ADR-006, ADR-009)."""
import json
import random
import time
import urllib.error
import urllib.request

from . import config


class LLMError(Exception):
    pass


class TooLarge(LLMError):
    pass


def est_tokens(obj):
    s = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return int(len(s) / 3.6) + 1


_SHARED = {"window": {}, "cooldown": {}, "rr": {}}    # one view of every key's usage per process


class Client:
    def __init__(self, role, log=print, tiers=None):
        self.role = role
        self.tiers = tiers or config.tiers(role)
        self.log = log
        self.window = _SHARED["window"]      # (provider, key index) -> [(time, tokens)]
        self.cooldown = _SHARED["cooldown"]  # (provider, key index) -> time until usable
        self.rr = _SHARED["rr"]
        self.tokens_used = 0
        self.calls = 0
        self.served = []        # tier label for every call (written to state.json)

    # -- key choice ---------------------------------------------------------
    def _pick_key(self, provider, need):
        keys = config.api_keys(provider)
        if not keys:
            raise LLMError("no API key for " + provider)
        if provider not in _SHARED.setdefault("announced", {}):
            _SHARED["announced"][provider] = len(keys)
            self.log("%s: %d API key(s) available" % (provider, len(keys)))
        now = time.time()
        order = [(self.rr.get(provider, 0) + i) % len(keys) for i in range(len(keys))]
        for i in order:
            ident = (provider, i)
            if self.cooldown.get(ident, 0) > now:
                continue
            if provider == "groq":
                recent = [x for x in self.window.get(ident, []) if x[0] > now - 60]
                self.window[ident] = recent
                if sum(t for _, t in recent) + need > config.GROQ_TPM_LIMIT:
                    continue
            self.rr[provider] = (i + 1) % len(keys)
            return i, keys[i]
        return None, None

    def _wait_for_key(self, provider, need):
        n = len(config.api_keys(provider))
        soonest = min([self.cooldown.get((provider, i), 0) for i in range(n)] or [0])
        if n and soonest - time.time() > 90:            # every key is set aside for a long time: give up on this tier now
            raise LLMError("every %s key is rate limited for another %.0f s" % (provider, soonest - time.time()))
        for _ in range(40):
            i, k = self._pick_key(provider, need)
            if k:
                return i, k
            time.sleep(3)
        raise LLMError("no key available for %s within 2 minutes" % provider)

    # -- one HTTP call ------------------------------------------------------
    def _post(self, provider, model, key, body):
        req = urllib.request.Request(
            config.PROVIDERS[provider] + "/chat/completions",
            json.dumps(body).encode(),
            {"Authorization": "Bearer " + key, "Content-Type": "application/json",
             "User-Agent": "autose/1.0"})
        with urllib.request.urlopen(req, timeout=config.BUDGET["call_timeout"][provider]) as r:
            return json.load(r)

    def chat(self, messages, tools=None, max_tokens=None, temperature=0.2):
        max_tokens = max_tokens or config.BUDGET["max_tokens"]
        prompt_est = est_tokens(messages) + (est_tokens(tools) if tools else 0)
        last = None
        for provider, model in self.tiers:
            label = provider + ":" + model
            mt = max_tokens
            if provider == "groq":
                mt = min(max_tokens, config.GROQ_TPM_LIMIT - prompt_est)
                if mt < min(400, max_tokens):          # only a prompt that leaves no room for the requested answer is too large
                    last = TooLarge("%s: prompt of about %d tokens leaves no room under the rate limit" % (label, prompt_est))
                    continue
            need = prompt_est + mt
            timeouts = 0
            for attempt in range(max(8, 2 * len(config.api_keys(provider)))):
                try:
                    idx, key = self._wait_for_key(provider, need)
                except LLMError as e:
                    last = e
                    break
                body = {"model": model, "messages": messages, "max_tokens": mt,
                        "temperature": temperature}
                if tools:
                    body["tools"] = tools
                if provider == "groq" and model.startswith("openai/gpt-oss"):
                    body["reasoning_effort"] = "low"
                ident = (provider, idx)
                t0 = time.time()
                self.window.setdefault(ident, []).append((time.time(), need))
                try:
                    d = self._post(provider, model, key, body)
                except urllib.error.HTTPError as e:
                    text = e.read().decode(errors="replace")[:400]
                    last = LLMError("%s HTTP %s %s" % (label, e.code, text[:400]))
                    if e.code in (401, 403):
                        self.log("key#%d of %s refused (HTTP %d): %s" % (idx, provider, e.code, text[:140].replace("\n", " ")))
                        self.cooldown[ident] = time.time() + (float("inf") if e.code == 401 else 600)
                        continue
                    if e.code == 429:
                        wait = float(e.headers.get("retry-after", 20) or 20)
                        if "per day" in text or "(TPD)" in text:      # daily quota: do not retry this key soon
                            wait = max(wait, 900)
                        self.cooldown[ident] = time.time() + min(wait, 3600)
                        self.log("key#%d of %s rate limited, set aside %.0fs: %s" % (idx, provider, min(wait, 3600), text[60:200].replace("\n", " ")))
                        continue
                    if e.code == 413 or "too large" in text.lower():
                        raise TooLarge(str(last))
                    self.window[ident][-1] = (time.time(), 200)      # a rejected request used almost nothing
                    if e.code == 400 and ("tool_use_failed" in text or "output_parse_failed" in text):
                        self.log("malformed tool call: " + text[:500].replace("\n", " "))
                        return {"role": "assistant", "content": "",
                                "_malformed_tool_call": True}, 0, label
                    if e.code in (500, 502, 503, 504):
                        time.sleep(2 + 2 * attempt + random.random())
                        continue
                    break           # other 4xx: try next tier
                except (urllib.error.URLError, TimeoutError, OSError) as e:
                    last = LLMError("%s %s" % (label, type(e).__name__))
                    timeouts += 1
                    self.log("%s: no answer within %ds (%s), attempt %d" % (label, config.BUDGET["call_timeout"][provider], type(e).__name__, timeouts))
                    if timeouts >= 4:               # an endpoint that hangs: give the tier up instead of waiting for minutes
                        break
                    time.sleep(2)
                    continue
                msg = d["choices"][0]["message"]
                used = d.get("usage", {}).get("total_tokens", need)
                self.log("call %s key#%d prompt~%d used %d in %.1fs" % (label, idx, prompt_est, used, time.time() - t0))
                self.window[ident][-1] = (time.time(), used)
                self.tokens_used += used
                self.calls += 1
                self.served.append(label)
                return msg, used, label
            self.log("tier failed, trying next: " + str(last))
        if isinstance(last, TooLarge):
            raise last
        raise LLMError("all tiers failed: %s" % last)

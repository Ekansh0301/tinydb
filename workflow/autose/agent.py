"""A small ReAct loop with hard budgets (ADR-009). The model chooses tools and
when to stop; code enforces call, token and loop limits."""
import json
import re
from dataclasses import dataclass, field

from . import config, llm, tools


@dataclass
class Result:
    text: str = ""
    stopped: str = ""            # "" when the agent finished by itself
    calls: int = 0
    tokens: int = 0
    transcript: list = field(default_factory=list)
    ran_command: bool = False
    reminded: bool = False
    wrapped: bool = False


def _compact(messages, budget):
    """Shrink old tool outputs first, then old assistant text, until the prompt fits."""
    def size():
        return llm.est_tokens(messages)
    if size() <= budget:
        return True
    for m in messages[2:]:
        if m["role"] == "tool" and len(m["content"]) > 80:
            m["content"] = "[earlier output omitted]"
            if size() <= budget:
                return True
    for m in messages[2:]:
        if m["role"] == "assistant" and m.get("content"):
            m["content"] = ""
            if size() <= budget:
                return True
    return size() <= budget


def run_agent(role, client, system, user, toolbox, stage_calls=None, stage_tokens=None,
              input_budget=None, max_tokens=None, must_edit=False, wrap_up_at=None):
    cap_calls = stage_calls or config.BUDGET["stage_calls"]
    cap_tokens = stage_tokens or config.BUDGET["stage_tokens"]
    schema = tools.schemas(role) if toolbox else None
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    res = Result()
    seen = {}
    nudges = 0
    while True:
        if res.calls >= cap_calls:
            res.stopped = "call budget exhausted (%d calls)" % cap_calls
            break
        if res.tokens >= cap_tokens:
            res.stopped = "token budget exhausted (%d tokens)" % res.tokens
            break
        if wrap_up_at and not res.wrapped and (res.calls >= wrap_up_at * cap_calls or res.tokens >= wrap_up_at * cap_tokens):
            res.wrapped = True
            messages.append({"role": "user", "content":
                             "Most of your budget is used. Give your final answer now, based on what you have found."})
        if not _compact(messages, input_budget or config.BUDGET["input_tokens"]):
            res.stopped = "context cannot be made to fit the request limit"
            break
        try:
            msg, used, label = client.chat(messages, schema, max_tokens=max_tokens,
                                           temperature=0.2 if nudges == 0 else 0.8)
        except llm.TooLarge:
            res.stopped = "request too large for the model limit"
            break
        except llm.LLMError as e:
            res.stopped = "model unavailable: %s" % e
            break
        res.calls += 1
        res.tokens += used
        if msg.get("_malformed_tool_call"):
            nudges += 1
            if nudges > 8:
                res.stopped = "model kept producing malformed tool calls"
                break
            if nudges % 2 == 0:          # first plain retry (sampling differs), then a reminder
                messages.append({"role": "user", "content":
                                 "Your last reply was malformed. Use only the tools you were given, with valid JSON "
                                 "arguments, or give your final answer."})
            continue
        calls = msg.get("tool_calls") or []
        clean = {"role": "assistant", "content": msg.get("content") or ""}
        if calls:
            clean["tool_calls"] = [{"id": c["id"], "type": "function",
                                    "function": {"name": c["function"]["name"],
                                                 "arguments": c["function"]["arguments"] or "{}"}}
                                   for c in calls[:4]]
        messages.append(clean)
        res.transcript.append({"model": label, "content": clean["content"],
                               "tool_calls": clean.get("tool_calls", [])})
        if not calls:
            if must_edit and toolbox is not None and toolbox.edits == 0 and not res.reminded:
                res.reminded = True      # describing a change in words is not making it
                messages.append({"role": "user", "content":
                                 "You have not changed any file yet. Make the change now with the edit_file or "
                                 "write_file tool; a description without edits counts as nothing."})
                continue
            res.text = (msg.get("content") or "").strip()
            break
        for c in clean["tool_calls"]:
            name = c["function"]["name"]
            try:
                args = json.loads(c["function"]["arguments"] or "{}")
                if not isinstance(args, dict):
                    raise ValueError
            except ValueError:
                out = "error: arguments are not a JSON object"
                args = {}
            else:
                key = (name, json.dumps(args, sort_keys=True))
                seen[key] = seen.get(key, 0) + 1
                if seen[key] >= 3:
                    res.stopped = "stuck: same tool call repeated 3 times"
                    out = "error: repeated call"
                else:
                    out = toolbox.call(name, args)
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": out})
            res.transcript.append({"tool": name, "args": args, "output": out[:600]})
        if res.stopped:
            break
    res.ran_command = bool(toolbox and toolbox.ran_command)
    return res

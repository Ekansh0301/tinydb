"""Latency and status of tool-calling requests to NVIDIA's endpoint, as seen from where this runs.

Used by .github/workflows/probe-models.yml. Each call sends a prompt of about 4,000 tokens with one
tool definition and asks for a tool call, like a tester or implementer step does. No key is printed.
"""
import json
import os
import time
import urllib.error
import urllib.request

KEY = os.environ["NVIDIA_API_KEY"]
MODELS = [m.strip() for m in os.environ.get("MODELS", "").split(",") if m.strip()]
CALLS = int(os.environ.get("CALLS", "6"))
TOOLS = [{"type": "function", "function": {"name": "open_file", "description": "Open a file",
          "parameters": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}}}]
FILLER = "def f(x):\n    return x + 1  # helper\n" * 220
MESSAGES = [{"role": "system", "content": "You are a coding agent. Use tools."},
            {"role": "user", "content": FILLER + "\nOpen tinydb/table.py with the tool."}]


def call(model, timeout=60):
    body = json.dumps({"model": model, "messages": MESSAGES, "tools": TOOLS, "max_tokens": 300}).encode()
    req = urllib.request.Request("https://integrate.api.nvidia.com/v1/chat/completions", body,
                                 {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t = time.time()
    try:
        d = json.load(urllib.request.urlopen(req, timeout=timeout))
        return ("tool" if d["choices"][0]["message"].get("tool_calls") else "text"), time.time() - t
    except urllib.error.HTTPError as e:
        return "HTTP%d" % e.code, time.time() - t
    except Exception as e:
        return type(e).__name__, time.time() - t


for m in MODELS:
    results = [call(m) for _ in range(CALLS)]
    print(m, " ".join("%s:%.1fs" % r for r in results), flush=True)

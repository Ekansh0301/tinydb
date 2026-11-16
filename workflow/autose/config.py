"""Settings in one place: budgets, model tiers, paths the agents may not touch."""
import os

REPO = "Ekansh0301/tinydb"          # the workflow refuses to run anywhere else
BASE_BRANCH = "main"
RUNS_BRANCH = "autose-runs"
LABEL = "autose"
MAX_FIX_CYCLES = 2          # review feedback sent back at most twice (so up to three reviews)

# Top-level paths agents can neither read nor write (ADR-009, ADR-003).
DENY = {"experiment", "architecture", "workflow", "results", ".github", ".git",
        "report.pdf", "README.md", "AI.md"}

BUDGET = {
    "input_tokens": 4500,       # estimated prompt size per request (Groq: 8000 tokens/min/key)
    "max_tokens": 1100,         # completion cap per request
    "tool_chars": 2600,         # cap on one tool output
    "stage_calls": 25,
    "stage_tokens": 60_000,
    "run_tokens": 400_000,
    "call_timeout": 90,
    "run_timeout": 120,         # seconds per tool command
}

PROVIDERS = {
    "groq": "https://api.groq.com/openai/v1",
    "nvidia": "https://integrate.api.nvidia.com/v1",
}

# ADR-006. Override with AUTOSE_TIERS_<ROLE>="provider:model,provider:model".
ROLE_TIERS = {
    "builder": [("groq", "openai/gpt-oss-120b")],
    "reviewer": [("nvidia", "nvidia/nemotron-3.5-super-vl-120b-a12b"),
                 ("nvidia", "nvidia/nemotron-3-ultra-550b-a55b"),
                 ("groq", "qwen/qwen3.8-27b")],
    "guard": [("groq", "meta-llama/llama-prompt-guard-2-86m")],
}
GROQ_TPM_LIMIT = 7000            # per key, with headroom below the 8000 limit
INJECTION_THRESHOLD = 0.9


def tiers(role):
    raw = os.environ.get("AUTOSE_TIERS_" + role.upper())
    if raw:
        return [tuple(x.strip().split(":", 1)) for x in raw.split(",") if x.strip()]
    return ROLE_TIERS[role]


def api_keys(provider):
    """Keys come from the environment (repository secrets); a local key file is
    read only when AUTOSE_KEYFILE is set, for development runs."""
    name = {"groq": "GROQ_API_KEY", "nvidia": "NVIDIA_API_KEY"}[provider]
    keys = [k.strip() for k in os.environ.get(name + "S", "").split(",") if k.strip()]
    keys += [v.strip() for k, v in os.environ.items()
             if k.startswith(name + "_") and v.strip()]
    if not keys and os.environ.get(name, "").strip():
        keys = [os.environ[name].strip()]
    kf = os.environ.get("AUTOSE_KEYFILE")
    if not keys and kf and os.path.exists(kf):
        for line in open(kf):
            if line.startswith(name) and "=" in line:
                keys.append(line.split("=", 1)[1].strip().strip("\"'"))
    return list(dict.fromkeys(keys))

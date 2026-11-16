# Model probe (2026-11-16, Groq free tier, 5 working keys)

Purpose: evidence for the model-choice decision (D6) before any agent code is written.
Models were called with the same prompts through the OpenAI-compatible endpoint. API keys are never logged.

| Model | Tool calls (8 trials, 2 tools) | Avg latency | Per-request limit | Notes |
|---|---|---|---|---|
| openai/gpt-oss-120b | 8/8 | 0.74 s | 8000 tokens per minute (TPM), request over limit is rejected | stable |
| qwen/qwen3.8-27b | 6/8 (2 "over capacity" errors) plus one malformed XML-style tool call seen in an earlier probe | 4.69 s | 7000 input tokens per minute | preview model, less reliable |
| openai/gpt-oss-20b | 1/1 simple call | about 0.5 s | 8000 TPM | spends its output budget on reasoning, sometimes returns empty content |

Prompt-injection classifiers (score for "injection"): llama-prompt-guard-2-86m gave 0.998 on an injected issue and 0.0004 on a benign one; the 22m model gave 0.989 and 0.002.

Reviewer smoke test (3 trials, diff only, no repository access): gpt-oss-120b returned REQUEST_CHANGES on all six trials including the harmless diff; qwen3.8-27b returned REQUEST_CHANGES on the buggy diff 3/3 and on the harmless diff 2/3. The harmless diff was a no-op comment change, so this is only a rough bias check. It is not evidence about review quality; that comes from the seeded-PR experiment.

## Consequences for the design
- Every single request must stay under about 7k tokens. Hand-offs must be compact artifacts, not full conversations, and file reads must be truncated.
- Keys are rotated per request. The limit applies per key and per model.
- Both providers must be retried with backoff. The reviewer needs a defined behaviour when its model is unavailable (stop and report, never approve by default).

## Gemini probe (2026-11-16, free tier, one key)

| Model | Result |
|---|---|
| gemini-3.8-flash | in the model list; 0 of 5 tool-call trials succeeded (503 "high demand" or 20 s timeout), then 1 of 3 simple calls returned 503 and 2 timed out |
| gemini-3.5-flash | 3 of 3 simple calls timed out at 12 s |
| gemini-2.5-flash | 404 on the OpenAI-compatible endpoint |

At probe time no Gemini model answered a single request. The reviewer therefore cannot depend on Gemini alone. Decision input for D6/D8: use Gemini as an optional primary only if a later probe shows it answering; the guaranteed path is the Groq reviewer, with a hard stop (never approve) if every reviewer is unavailable.

## NVIDIA build.nvidia.com probe (2026-11-16, free endpoint, one key)

Round 1: 4 tool-call trials per model, 40 s timeout. kimi-k3.1-pro is not served on this key (not in `/v1/models`).

| Model | Tool calls ok | Notes |
|---|---|---|
| nvidia/nemotron-3.5-super-vl-120b-a12b | 4/4 | avg 1.6 s |
| nvidia/nemotron-3-ultra-550b-a55b | 4/4 | avg 2.0 s |
| poolside/laguna-xs-2.1 | 4/4 | avg 5.5 s |
| mistralai/mistral-large-4-1t-a52b | 3/4 | one timeout |
| nvidia/nemotron-3.5-lightning-30b-a3b | 2/4 | two replies without a tool call |
| stepfun-ai/step-5-preview | 1/4 | slow, timeouts |
| minimaxai/minimax-m3.1-flash | 1/4 | three 503 |
| google/gemma-4-31b-it, deepseek-ai/deepseek-v4.1-flash, z-ai/glm-5.3-flash | 0/4 | all timed out |

Round 2 (top four): review of a correct diff and a subtly wrong diff (upper bound exclusive instead of inclusive), 3 trials each, plus one 20k-token request.

| Model | correct diff | wrong diff | 20k-token request |
|---|---|---|---|
| nemotron-3.5-super-vl-120b | APPROVE 3/3 | REQUEST_CHANGES 3/3 | accepted, 1.0 s |
| nemotron-3-ultra-550b | APPROVE 3/3 | REQUEST_CHANGES 3/3 | accepted, 2.0 s |
| laguna-xs-2.1 | APPROVE 3/3 | caught 2/3 (one APPROVE) | accepted, 1.1 s |
| mistral-large-4 | 2/3 answered (one timeout) | 2/3 answered, both caught | accepted, 4.8 s |

Caveats: three trials per cell is a smoke test, not a measurement. Both Nemotron models come from the same vendor, so using one as fallback for the other gives less independence than a different vendor. Free-endpoint request-per-minute limits and "early access" model availability were not measured.

# Issue in, pull request out: an agentic SDLC workflow on a tinydb fork

This repository is a fork of [msiemens/tinydb](https://github.com/msiemens/tinydb) with a GitHub Actions
workflow in which agents turn an issue into a tested and reviewed pull request, and the design records
that explain why it is built this way. It is the submission for assignment 3 (roll number 2023114007).

## Repository and commit

| | |
|---|---|
| Fork | https://github.com/Ekansh0301/tinydb |
| Upstream project and pinned commit | `msiemens/tinydb` at `edff96aeb2616402e9489d46e90a592c05565621` (`edff96a`) |
| Prepared base (documentation removed, `ARCHITECTURE.md` added) | `8a94233df3249e9dcbfa072b4d11b9dc0acaec13` (list of removed files: `experiment/removed_files.txt`) |
| Baseline test suite | 228 passed, 0 failed, 0 skipped |
| `main` | protected: pull requests only, no direct pushes, no force pushes, applies to administrators |

## Models

| Role | Model (provider) |
|---|---|
| Planner (stages 1 and 2), implementer (stage 3) | `openai/gpt-oss-120b` (Groq), fallback `poolside/laguna-xs-2.1` (NVIDIA) |
| Tester (stage 4) | `poolside/laguna-xs-2.1` (NVIDIA), fallback `gpt-oss-120b` |
| Reviewer (stage 6) | `nvidia/nemotron-3.5-super-vl-120b-a12b`, then `nemotron-3-ultra-550b-a55b`, then `qwen/qwen3.8-27b` (Groq) |
| Prompt-injection screen | `meta-llama/llama-prompt-guard-2-86m` (Groq) |

All are free tiers; the spending limit is therefore zero. Reasons and measurements: `architecture/decisions/ADR-006.md`
and `experiment/model_probe.md`.

## How to trigger the workflow

1. Open an issue in this fork.
2. A maintainer (write access) adds the label **`autose`**, or comments **`/autose`** on the issue.
3. The run goes through: `gate` (who may start it, other run active, prompt-injection screen) →
   `build` (stages 1 to 5, opens the pull request) → `ci` (reusable workflow on the PR head) →
   `review` (stage 6, separate read-only job, other model) → `next` (posts the review; asks for another
   round at most twice, or stops).
4. Follow it through: the Actions run, the pull request and its review comment, and the artifacts of every stage on the
   branch `autose-runs` under `runs/issue-<N>/round-<R>/` (`spec.md`, `design.md`, `diff.patch`, `test_report.md`,
   `pr.md`, `review.md`, `state.json`, a log and the agent transcripts).
5. A person decides to merge or close. The workflow has no merge step and no token that could merge.

A comment `/autose` on an open autose pull request asks for a fresh review of that pull request only.

## Layout

```
README.md
report.pdf
architecture/
  views/          component view, planned and real sequence view, stage map (agent, artifact, check)
  decisions/      ADR-001 ... one per decision; superseded ones are kept and marked
workflow/
  autose/         orchestrator, agents, tools, gates, model client, entry points
  prompts/        the prompt of every agent
  tests/          unit tests for tools, gates, routing and model-tier fallback
  github-workflows/   copy of .github/workflows/
experiment/
  issues/         the five issue texts
  hidden_tests/   acceptance tests (added after the runs, see below)
  seeded_prs/     the five reviewer-check pull requests: diffs and labels
  variants.md     what each decision-experiment variant changes
  score.py        scores a result against the hidden tests and the baseline
  model_probe.md  availability and tool-call measurements behind the model choices
results/
  results.csv
  runs.md         links to every Actions run, pull request and review
```

## Hidden tests

Each of the five issues has two to four hidden acceptance tests (22 in total). They were written before any run, validated
against a reference fix (all fail on the base commit except regression guards, all pass on the fix), and kept outside this
repository while the agents could still read it. They are added to `experiment/hidden_tests/` after the last run.
Scoring: `python experiment/score.py --issue <1..5> --branch autose/issue-<N>`.

## Rules followed

- The workflow acts only on `Ekansh0301/tinydb`; it refuses to run in any other repository and never pushes to the upstream project.
- It never merges.
- API keys are repository secrets (`GROQ_API_KEYS`, `NVIDIA_API_KEY`). They are not in code, logs or prompts; commands run by
  agents start with an empty environment.
- Total tokens used: see `results/runs.md`.

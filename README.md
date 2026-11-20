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
| Planner (stages 1 and 2), implementer (stage 3) | `openai/gpt-oss-120b` (Groq) |
| Tester (stage 4) | `openai/gpt-oss-20b` (Groq) |
| Reviewer (stage 6) | `nvidia/nemotron-3-ultra-550b-a55b`, then `nemotron-3.5-super-vl-120b-a12b`, then `qwen/qwen3.8-27b` (Groq); the recorded pipeline reviews used `3.5-super` first (see ADR-008) |
| Prompt-injection screen | `meta-llama/llama-prompt-guard-2-86m` (Groq) |

All are free tiers; the spending limit is therefore zero. Reasons and measurements: `architecture/decisions/ADR-012.md` (history: ADR-006)
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

CI for a pull request opened by the workflow runs inside the same Actions run (job `ci / tests`, a reusable workflow on the PR head); GitHub does not start the ordinary `pull_request` check for a pull request created with the workflow token, so the three autose pull requests were closed and reopened once by hand to attach that check to the page.

The label trigger and the issue comment were used on issue #7 (the first runs); the later recorded runs were started with
`workflow_dispatch` through `experiment/drive.py`, which runs the same jobs. Each review round is started by the workflow itself
(`next` dispatches the following round), never by hand, except one hand-off that the gate refused because of a bug (`runs.md`).

## Reuse of the earlier assignments

- **Stage 1 reuses the requirements skill of assignment 1.** `workflow/prompts/spec.md` is a condensed, non-interactive version of it: source statements, a status on every requirement (STATED, INFERRED, ASSUMED), `shall` only for stated requirements, Given/When/Then criteria with a concrete outcome, and no invented requirements. The interactive questions and the confidence score of that skill are dropped, because no stakeholder can answer inside a run.
- **Stage 2 uses the `ARCHITECTURE.md` of assignment 2** (tinydb at the same commit): components, three ADRs and five constraints. The design stage receives it trimmed to the component table, the ADR decisions and the constraints (`architecture/decisions/ADR-011.md`).

## Results at a glance

| | |
|---|---|
| Pipeline on the five issues | pull request on three (#4: 4/4 hidden tests; #6: 4/4; #7: 2/4, then 3/4 after the review round); #5 stopped at stage 4 and #8 at stage 2 (model results) |
| Reviewer | asked for changes twice (a real cache defect on #7, dead code on #6); approved after round 2 |
| E1 split versus one agent | pipeline: 3 of 5 issues reach a pull request; one agent: 0 of 5 (never passed the test gate) |
| E2 reviewer independence | independent reviewer caught 8 of 9 defective seeded PRs and approved 6 of 6 correct ones; the builder's own model caught 1 of 9 |
| E2b larger reviewer (bonus) | the 550B reviewer: 15 of 15 valid reviews, 9 of 9 caught, 6 of 6 approved, at twice the tokens |
| Prompt injection | the screen caught blunt injections (0.99) and missed polite ones; in an end-to-end test the agents treated an unscreened polite injection as data. The test also found that the screen had been failing open and that an error message leaked a short-lived token; both fixed (ADR-009, `experiment/injection_test.md`) |

Details, per-stage pass rates and the reasoning: `report.pdf`, `results/`, `architecture/decisions/`.

## Frozen version and run protocol

The workflow code, prompts, gates and model assignment used for the recorded runs are tagged **`autose-v1`** (commit `de625a2`); one crash fix after the first runs is tagged `autose-v1.1` (ADR-007 amendment). Later tags: `autose-v1.2` reviewer order (after the recorded runs, ADR-008), `autose-v1.3` injection screen fixed and fail-closed, `autose-v1.4` credentials redacted from messages, `autose-v1.5` named variants keep the review rounds (all in ADR-009 and `experiment/protocol.md`).
`experiment/protocol.md` says what was fixed before the remaining runs, what counts as a rerun, and the token budget;
`experiment/rehearsal.md` records the development runs that preceded the freeze; every attempt, including stopped and cancelled
ones, is listed with a note in `results/runs.md`.

## Scripts

| Script | What it does |
|---|---|
| `experiment/drive.py <issue> [--variant single]` | starts one recorded run and waits until it and its review rounds finish |
| `experiment/score.py --issue <1..5> --branch <b> [--sha <s>]` | hidden acceptance tests and the 228 baseline tests |
| `experiment/collect.py` | builds `results/runs.md`, `results.csv`, `seeded.csv`, `stage_pass_rates.csv` from GitHub and the `autose-runs` branch |
| `experiment/tokens.py` | token totals by model from the logs of every run |
| `report/build.py` | builds `report.pdf` from `results/*.csv` (xelatex) |

## Layout

```
README.md
report.pdf
architecture/
  views/          component view, sequence view of a real run, stage map (agent, artifact, check)
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
  protocol.md     frozen code, rerun rule, experiments, token budget (with amendments)
  rehearsal.md    development runs before the freeze
  injection_test.md / .py   the prompt-injection tests and what they found
  score.py drive.py collect.py tokens.py   scoring, running, collecting results and tokens
  model_probe.md  availability and tool-call measurements behind the model choices
results/
  results.csv  seeded.csv  stage_pass_rates.csv  tokens.csv
  runs.md         links to every Actions run, pull request and review (with a note each)
report/           sources of report.pdf (build.py, report.tex, figures, text)
```

## Hidden tests

Each of the five issues has four hidden acceptance tests (20 in total). They were written before any run, validated
against a reference fix (16 fail on the base commit, the other 4 are regression guards, all 20 pass on the fix), and kept outside this
repository while the agents could still read it. They were added to `experiment/hidden_tests/` after the last recorded run.
Scoring: `python experiment/score.py --issue <1..5> --branch autose/issue-<N>`.

## Rules followed

- The workflow acts only on `Ekansh0301/tinydb`; it refuses to run in any other repository and never pushes to the upstream project.
- It never merges.
- API keys are repository secrets (`GROQ_API_KEYS`, `NVIDIA_API_KEY`). They are not in code, logs or prompts; commands run by
  agents start with an empty environment; anything logged, stored or commented passes through `redact` (one earlier lapse is recorded in ADR-009).
- Token use: `results/tokens.csv` and the appendix of `report.pdf` (counted from the logs of every Actions run; a lower bound).

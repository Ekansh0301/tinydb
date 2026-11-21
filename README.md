# Issue in, pull request out: an agentic SDLC workflow on a tinydb fork

A GitHub Actions workflow in which agents turn an issue into a tested and reviewed pull request, on a fork of
[msiemens/tinydb](https://github.com/msiemens/tinydb), together with the design records that explain why it is built this way.
Submission for assignment 3 (AutoSE), roll number 2023114007.

**Contents:** [At a glance](#at-a-glance) · [Demo video](#demo-video) · [How it works](#how-it-works) · [Models](#models) ·
[How to trigger it](#how-to-trigger-the-workflow) · [Results](#results-at-a-glance) · [Design decisions](#design-decisions) ·
[Reproducing](#reproducing-and-scripts) · [Repository layout](#repository-layout) · [Hidden tests](#hidden-tests) ·
[Frozen version](#frozen-version-and-run-protocol) · [Rules followed](#rules-followed) · [AI assistance](#ai-assistance)

## At a glance

| | |
|---|---|
| Fork | https://github.com/Ekansh0301/tinydb |
| Upstream project and pinned commit | `msiemens/tinydb` at `edff96aeb2616402e9489d46e90a592c05565621` (`edff96a`) |
| Prepared base (documentation removed, `ARCHITECTURE.md` added) | `8a94233df3249e9dcbfa072b4d11b9dc0acaec13` (list of removed files: `experiment/removed_files.txt`) |
| Baseline test suite | 228 passed, 0 failed, 0 skipped |
| `main` | protected: pull requests only, no direct pushes, no force pushes, applies to administrators |
| Report | [`report.pdf`](report.pdf) (7 pages plus appendix) |
| Video | [`demo.mp4`](demo.mp4) (4 min 29 s) |
| Cost | all models are free tiers, so the spending limit is zero; token use is reported in `results/tokens.csv` |

## Demo video

[`demo.mp4`](demo.mp4) (subtitles only) shows one complete run, live, from the issue page to the posted review:
issue #75 is created, the label `autose` is added, and each job (gate, build, ci, review, next) is opened while it runs.
The reviewer asked for changes in round 1 (dead code the tests cannot see) and approved in round 2, which the `next` job started by itself.
The build and review waits are sped up and marked as such; the stage tracker, clock and token counter on screen are drawn from the run's own
records (`stages.jsonl`, job timings). Run [44931285607](https://github.com/Ekansh0301/tinydb/actions/runs/44931285607) (round 1),
[44932673974](https://github.com/Ekansh0301/tinydb/actions/runs/44932673974) (round 2), pull request #76, left open for a person to decide.
Earlier recording takes (issues #71 and #73) are closed and listed in `results/runs.md`. These runs are not part of the results tables.

## How it works

Six fixed stages, each saving an artifact and handing over only after a check written in code (`workflow/autose/gates.py`) has passed.
An agent never decides that its own work is good enough, and never chooses the next stage: a plain-Python orchestrator owns the state machine,
the back-edges and the budgets.

| # | Stage | Agent (model) | Artifact | Check before moving on | On failure |
|---|---|---|---|---|---|
| 1 | Requirements | Planner (`gpt-oss-120b`) | `spec.md` | required sections, Given/When/Then criteria with a concrete outcome, every requirement has a criterion | 3 attempts, then stop |
| 2 | Design | Planner | `design.md` | every file and function named exists or is marked NEW; every criterion has a row | 3 attempts, then stop |
| 3 | Implementation | Implementer (`gpt-oss-120b`) | `diff.patch` | diff not empty, only designed files changed, compiles and imports | 3 attempts in all |
| 4 | Testing | Tester (`gpt-oss-20b`) | `test_report.md` | a `test_ac<N>` per criterion, a new test fails on the base commit, the whole suite passes | back to stage 3; the same criterion twice: back to stage 1 |
| 5 | Release | none (code) | `pr.md` and the PR link | PR open, CI green on its head | stop and report |
| 6 | Review | Reviewer (Nemotron, separate job) | `review.md` | valid JSON, at least two checks with evidence, a command was run | `approach`: back to 2, `code`: back to 3, at most two fix rounds |

- **Jobs:** `gate` (who may start it, no other run active, prompt-injection screen) → `build` (stages 1 to 5, the only job that may push) →
  `ci` (reusable workflow on the PR head) → `review` (separate job, `contents: read`, own model, sees only the issue, the diff and the repository) →
  `next` (posts the review and starts the next round, or ends).
- **State:** artifacts per stage live on the branch `autose-runs` under `runs/issue-<N>/round-<R>/` and as workflow artifacts, so a pull request holds only code.
- **Safety:** issue text reaches agents only as delimited data; agents have no network, no push and no secrets (commands run with an empty environment);
  every budget and timeout is bounded; the workflow refuses to run in any repository other than this fork and has no merge step.
- Views: `architecture/views/` (component view, sequence view of a real run, stage map).

## Models

| Role | Model (provider) |
|---|---|
| Planner (stages 1 and 2), implementer (stage 3) | `openai/gpt-oss-120b` (Groq) |
| Tester (stage 4) | `openai/gpt-oss-20b` (Groq) |
| Reviewer (stage 6) | `nvidia/nemotron-3-ultra-550b-a55b`, then `nemotron-3.5-super-vl-120b-a12b`, then `qwen/qwen3.8-27b` (Groq); the recorded pipeline reviews used `3.5-super` first (see ADR-008) |
| Prompt-injection screen | `meta-llama/llama-prompt-guard-2-86m` (Groq) |

Reasons and measurements: `architecture/decisions/ADR-012.md` (history: ADR-006) and `experiment/model_probe.md`.

## How to trigger the workflow

1. Open an issue in this fork.
2. A maintainer (write access) adds the label **`autose`**, or comments **`/autose`** on the issue.
3. The run goes through the jobs above. At most two fix rounds follow a review that asks for changes.
4. Follow it through: the Actions run, the pull request and its review comment, and the artifacts of every stage on the branch `autose-runs`
   (`spec.md`, `design.md`, `diff.patch`, `test_report.md`, `pr.md`, `review.md`, `state.json`, a log and the agent transcripts).
5. A person decides to merge or close. The workflow has no merge step and no token that could merge.

A comment `/autose` on an open autose pull request asks for a fresh review of that pull request only.

CI for a pull request opened by the workflow runs inside the same Actions run (job `ci / tests`, a reusable workflow on the PR head); GitHub does not start the ordinary `pull_request` check for a pull request created with the workflow token, so the three autose pull requests were closed and reopened once by hand to attach that check to the page.

The label trigger and the issue comment were used on issue #7 (the first runs) and the label again for the demo run (issue #75); the other recorded runs were started with
`workflow_dispatch` through `experiment/drive.py`, which runs the same jobs. Each review round is started by the workflow itself
(`next` dispatches the following round), never by hand, except one hand-off that the gate refused because of a bug (`results/runs.md`).

## Results at a glance

| | |
|---|---|
| Pipeline on the five issues | pull request on three (#4: 4/4 hidden tests; #6: 4/4; #7: 2/4, then 3/4 after the review round); #5 stopped at stage 4 and #8 at stage 2 (model results) |
| Reviewer | asked for changes twice (a real cache defect on #7, dead code on #6); approved after round 2 |
| E1 split versus one agent | pipeline: 3 of 5 issues reach a pull request; one agent: 0 of 5 (never passed the test gate) |
| E2 reviewer independence | independent reviewer caught 8 of 9 defective seeded PRs and approved 6 of 6 correct ones; the builder's own model caught 1 of 9 |
| E2b larger reviewer (bonus) | the 550B reviewer: 15 of 15 valid reviews, 9 of 9 caught, 6 of 6 approved, at twice the tokens |
| Prompt injection | the screen caught blunt injections (0.99) and missed polite ones; in an end-to-end test the agents treated an unscreened polite injection as data. The test also found that the screen had been failing open and that an error message leaked a short-lived token; both fixed (ADR-009, `experiment/injection_test.md`) |

Details, per-stage pass rates and the reasoning: `report.pdf`, `results/`, `architecture/decisions/`. Every Actions run, pull request and review is linked in `results/runs.md`.

## Design decisions

Twelve records in `architecture/decisions/` (Nygard format). Superseded ones are kept, marked, and replaced by a new record.

| ADR | Decision area | Status |
|---|---|---|
| [001](architecture/decisions/ADR-001.md) | D1 how the work is split | accepted, tested by E1 |
| [002](architecture/decisions/ADR-002.md) | D2 control flow: state machine, bounded back-edges | accepted |
| [003](architecture/decisions/ADR-003.md) | D3 hand-offs: artifacts, never conversations | superseded in part by 011 |
| [004](architecture/decisions/ADR-004.md) | D4 state: the `autose-runs` branch | accepted |
| [005](architecture/decisions/ADR-005.md) | D5 tools and permissions per role | accepted |
| [006](architecture/decisions/ADR-006.md) | D6 models, chosen from laptop probes | superseded by 012 |
| [007](architecture/decisions/ADR-007.md) | D7 stage checks are code | accepted |
| [008](architecture/decisions/ADR-008.md) | D8 reviewer independence | accepted, tested by E2 and E2b |
| [009](architecture/decisions/ADR-009.md) | D9 safety: budgets, bounded loops, untrusted input | accepted |
| [010](architecture/decisions/ADR-010.md) | D10 triggers, who may start a run, concurrency | accepted |
| [011](architecture/decisions/ADR-011.md) | D3 trimmed architecture note for the design stage | accepted, supersedes the planner row of 003 |
| [012](architecture/decisions/ADR-012.md) | D6 final model assignment | accepted, supersedes 006 |

## Reuse of the earlier assignments

- **Stage 1 reuses the requirements skill of assignment 1.** `workflow/prompts/spec.md` is a condensed, non-interactive version of it: source statements, a status on every requirement (STATED, INFERRED, ASSUMED), `shall` only for stated requirements, Given/When/Then criteria with a concrete outcome, and no invented requirements. The interactive questions and the confidence score of that skill are dropped, because no stakeholder can answer inside a run.
- **Stage 2 uses the `ARCHITECTURE.md` of assignment 2** (tinydb at the same commit): components, three ADRs and five constraints. The design stage receives it trimmed to the component table, the ADR decisions and the constraints (`architecture/decisions/ADR-011.md`).

## Reproducing and scripts

Tests (no keys needed):

```bash
python -m pytest tests -q                                                              # the tinydb library, 228 tests
PYTHONPATH=workflow python -m pytest workflow/tests -p no:cacheprovider -q -o addopts=   # the workflow code, 54 tests
```

Running the workflow needs the repository secrets `GROQ_API_KEYS` and `NVIDIA_API_KEY`, and it only runs in `Ekansh0301/tinydb`
(`REPO` in `workflow/autose/config.py`). A local rehearsal of stages 1 to 4 without GitHub:
`cd workflow && python -m autose local --repo .. --issue ../experiment/issues/<file>.md --number <n> [--review]`,
with the keys in the environment or in a key file named by `AUTOSE_KEYFILE`.

| Script | What it does |
|---|---|
| `experiment/drive.py <issue> [--variant single]` | starts one recorded run and waits until it and its review rounds finish |
| `experiment/score.py --issue <1..5> --branch <b> [--sha <s>]` | hidden acceptance tests and the 228 baseline tests |
| `experiment/collect.py` | builds `results/runs.md`, `results.csv`, `seeded.csv`, `stage_pass_rates.csv` from GitHub and the `autose-runs` branch |
| `experiment/tokens.py` | token totals by model from the logs of every run |
| `report/build.py` | builds `report.pdf` from `results/*.csv` (xelatex) |

## Repository layout

```
README.md
report.pdf         the report (sources in report/)
demo.mp4           screen recording of one live run (see Demo video)
ARCHITECTURE.md    architecture document from assignment 2, given to the design stage
architecture/
  views/           component view, sequence view of a real run, stage map (agent, artifact, check)
  decisions/       ADR-001 ... ADR-012; superseded ones are kept and marked
workflow/
  autose/          orchestrator, agents, tools, gates, model client, entry points
  prompts/         the prompt of every agent
  tests/           unit tests for tools, gates, routing and model-tier fallback
  github-workflows/   copy of .github/workflows/
.github/workflows/ the workflows that run (autose, ci, review-seeded, probe-models)
experiment/
  issues/          the five issue texts
  hidden_tests/    acceptance tests (added after the runs, see below)
  seeded_prs/      the five reviewer-check pull requests: diffs and labels
  variants.md      what each decision-experiment variant changes
  protocol.md      frozen code, rerun rule, experiments, token budget (with amendments)
  rehearsal.md     development runs before the freeze
  injection_test.md / .py   the prompt-injection tests and what they found
  model_probe.md   availability and tool-call measurements behind the model choices
  score.py drive.py collect.py tokens.py   scoring, running, collecting results and tokens
results/
  results.csv  seeded.csv  stage_pass_rates.csv  tokens.csv
  runs.md          links to every Actions run, pull request and review (with a note each)
report/            sources of report.pdf (build.py, report.tex, figures, text)
tinydb/  tests/    the library under test and its own tests, identical to the pinned upstream commit
```

## Hidden tests

Each of the five issues has four hidden acceptance tests (20 in total). They were written before any run, validated
against a reference fix (16 fail on the base commit, the other 4 are regression guards, all 20 pass on the fix), and kept outside this
repository while the agents could still read it. They were added to `experiment/hidden_tests/` after the last recorded run.
Scoring: `python experiment/score.py --issue <1..5> --branch autose/issue-<N>`.

## Frozen version and run protocol

The workflow code, prompts, gates and model assignment used for the recorded runs are tagged **`autose-v1`**.

| Tag | Commit | What changed |
|---|---|---|
| `autose-v1` | `de625a2` | frozen code for the recorded runs |
| `autose-v1.1` | `286f876` | crash fix: a directory in the design file column (ADR-007 amendment) |
| `autose-v1.2` | `7ffd0cb` | reviewer order, after the recorded runs (ADR-008) |
| `autose-v1.3` | `9957591` | injection screen fixed and fail-closed (ADR-009) |
| `autose-v1.4` | `116de68` | credentials redacted from messages (ADR-009) |
| `autose-v1.5` | `5b00fe4` | named variants keep the review rounds |

`experiment/protocol.md` says what was fixed before the remaining runs, what counts as a rerun, and the token budget;
`experiment/rehearsal.md` records the development runs that preceded the freeze; every attempt, including stopped and cancelled
ones, is listed with a note in `results/runs.md`.

## Rules followed

- The workflow acts only on `Ekansh0301/tinydb`; it refuses to run in any other repository and never pushes to the upstream project.
- It never merges.
- API keys are repository secrets (`GROQ_API_KEYS`, `NVIDIA_API_KEY`). They are not in code, logs or prompts; commands run by
  agents start with an empty environment; anything logged, stored or commented passes through `redact` (one earlier lapse is recorded in ADR-009).
- Token use: `results/tokens.csv` and the appendix of `report.pdf` (counted from the logs of every Actions run; a lower bound).

## AI assistance

AI was used for coding assistance.

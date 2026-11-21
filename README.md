# Issue in, pull request out: an agentic SDLC workflow on a tinydb fork

A GitHub Actions workflow in which agents turn an issue into a tested and reviewed pull request, on a fork of
[msiemens/tinydb](https://github.com/msiemens/tinydb), with the design records that explain why it is built this way.
Assignment 3 (AutoSE), roll number 2023114007.

| | |
|---|---|
| Fork | https://github.com/Ekansh0301/tinydb |
| Pinned upstream commit | `msiemens/tinydb` at `edff96aeb2616402e9489d46e90a592c05565621` |
| Prepared base (documentation removed, `ARCHITECTURE.md` added) | `8a94233df3249e9dcbfa072b4d11b9dc0acaec13` |
| Baseline tests | 228 passed |
| `main` | protected: pull requests only, no force pushes, applies to administrators |
| Report | [`report.pdf`](report.pdf) |
| Demo video | [`demo.mp4`](demo.mp4) (4 min 29 s) |
| Cost | free model tiers only, so the spending limit is zero; tokens in `results/tokens.csv` |

## How it works

Six stages. Each saves an artifact and hands over only after a check written in code (`workflow/autose/gates.py`) has passed.
A plain-Python orchestrator owns the state machine, the back-edges and the budgets; an agent never chooses the next stage.

| # | Stage | Agent | Artifact | Check before moving on | On failure |
|---|---|---|---|---|---|
| 1 | Requirements | Planner | `spec.md` | required sections, Given/When/Then criteria, every requirement has a criterion | 3 attempts, then stop |
| 2 | Design | Planner | `design.md` | files and functions named exist or are marked NEW; every criterion has a row | 3 attempts, then stop |
| 3 | Implementation | Implementer | `diff.patch` | diff not empty, only designed files changed, compiles | 3 attempts in all |
| 4 | Testing | Tester | `test_report.md` | a `test_ac<N>` per criterion, one fails on the base commit, whole suite passes | back to 3; same criterion twice: back to 1 |
| 5 | Release | none (code) | `pr.md` and PR link | PR open, CI green | stop and report |
| 6 | Review | Reviewer (separate job) | `review.md` | valid JSON, two or more checks with evidence, a command was run | `approach`: back to 2, `code`: back to 3, at most two fix rounds |

Jobs: `gate` (permission, no run active, injection screen) → `build` (stages 1 to 5) → `ci` → `review` (read-only, own model, sees only the issue, the diff and the repository) → `next` (posts the review, starts the next round or ends).
Artifacts per stage are kept on the branch `autose-runs` (`runs/issue-<N>/round-<R>/`), so a pull request holds only code. The workflow has no merge step.
Views: `architecture/views/`.

## Models

| Role | Model (provider) |
|---|---|
| Planner, implementer | `openai/gpt-oss-120b` (Groq) |
| Tester | `openai/gpt-oss-20b` (Groq) |
| Reviewer | `nvidia/nemotron-3-ultra-550b-a55b`, then `nemotron-3.5-super-vl-120b-a12b`, then `qwen/qwen3.8-27b` (the recorded pipeline reviews used `3.5-super` first, see ADR-008) |
| Injection screen | `meta-llama/llama-prompt-guard-2-86m` (Groq) |

Reasons and measurements: `architecture/decisions/ADR-012.md`, `experiment/model_probe.md`.

## How to trigger it

1. Open an issue in this fork.
2. A maintainer (write access) adds the label **`autose`** or comments **`/autose`**.
3. The jobs above run; a review that asks for changes starts at most two fix rounds.
4. Follow it in the Actions run, the pull request and its review comment, and the artifacts on `autose-runs`.
5. A person decides to merge or close.

`/autose` on an open autose pull request asks for a fresh review of that pull request only. CI for a pull request opened by the workflow runs inside the same Actions run (`ci / tests`), because GitHub does not start the ordinary pull request check for a pull request created with the workflow token (the three baseline pull requests were closed and reopened once by hand to attach that check to the page).

## Results

| | |
|---|---|
| Pipeline on the five issues | pull request on three (#4: 4/4 hidden tests, #6: 4/4, #7: 2/4, then 3/4 after review); #5 stopped at stage 4, #8 at stage 2 |
| E1 split vs one agent | pipeline: 3 of 5 issues reach a pull request; one agent: 0 of 5 |
| E2 reviewer independence | independent reviewer caught 8 of 9 defective seeded PRs and approved 6 of 6 correct ones; the builder's own model caught 1 of 9 |
| E2b larger reviewer | 550B reviewer: 9 of 9 caught, 6 of 6 approved, at twice the tokens |
| Prompt injection | the screen caught blunt injections and missed polite ones; the other layers held in an end-to-end test (ADR-009, `experiment/injection_test.md`) |

Per-stage pass rates, analysis and limitations: `report.pdf`. Every Actions run, pull request and review is linked in `results/runs.md`.

## Design decisions

| ADR | Decision | Status |
|---|---|---|
| [001](architecture/decisions/ADR-001.md) | D1 how the work is split | accepted, tested by E1 |
| [002](architecture/decisions/ADR-002.md) | D2 control flow | accepted |
| [003](architecture/decisions/ADR-003.md) | D3 hand-offs | superseded in part by 011 |
| [004](architecture/decisions/ADR-004.md) | D4 state | accepted |
| [005](architecture/decisions/ADR-005.md) | D5 tools and permissions | accepted |
| [006](architecture/decisions/ADR-006.md) | D6 models (first choice) | superseded by 012 |
| [007](architecture/decisions/ADR-007.md) | D7 stage checks | accepted |
| [008](architecture/decisions/ADR-008.md) | D8 reviewer independence | accepted, tested by E2 and E2b |
| [009](architecture/decisions/ADR-009.md) | D9 safety and failures | accepted |
| [010](architecture/decisions/ADR-010.md) | D10 triggers and concurrency | accepted |
| [011](architecture/decisions/ADR-011.md) | D3 trimmed architecture note | accepted, supersedes part of 003 |
| [012](architecture/decisions/ADR-012.md) | D6 final model assignment | accepted, supersedes 006 |

## Repository layout

```
README.md  report.pdf  demo.mp4
ARCHITECTURE.md    architecture document from assignment 2, given to the design stage
architecture/      views/ (component, sequence, stage map) and decisions/ (ADR-001 to ADR-012)
workflow/          autose/ (orchestrator, agents, tools, gates), prompts/, tests/, github-workflows/ (copy of .github/workflows/)
.github/workflows/ autose, ci, review-seeded, probe-models
experiment/        issues/, hidden_tests/, seeded_prs/, variants.md, protocol.md, rehearsal.md, injection_test.md, model_probe.md, scripts
results/           results.csv, seeded.csv, stage_pass_rates.csv, tokens.csv, runs.md
report/            sources of report.pdf
tinydb/  tests/    the library and its tests, identical to the pinned upstream commit
```

## Reproducing

```bash
python -m pytest tests -q                                                              # library, 228 tests
PYTHONPATH=workflow python -m pytest workflow/tests -p no:cacheprovider -q -o addopts=   # workflow code, 54 tests
```

Running the workflow needs the repository secrets `GROQ_API_KEYS` and `NVIDIA_API_KEY` and only works in `Ekansh0301/tinydb` (`REPO` in `workflow/autose/config.py`).
Scripts: `experiment/drive.py` (start a recorded run), `score.py` (hidden tests), `collect.py` (results tables), `tokens.py` (token totals), `report/build.py` (report).

## Hidden tests

Each of the five issues has four hidden acceptance tests (20 in total). They were written before any run, validated
against a reference fix (16 fail on the base commit, the other 4 are regression guards, all 20 pass on the fix), and kept outside this
repository while the agents could still read it. They were added to `experiment/hidden_tests/` after the last recorded run.
Scoring: `python experiment/score.py --issue <1..5> --branch autose/issue-<N>`.

## Reuse of the earlier assignments

- **Stage 1 reuses the requirements skill of assignment 1** (`workflow/prompts/spec.md`): a condensed, non-interactive version with source statements, a status per requirement (STATED, INFERRED, ASSUMED) and Given/When/Then criteria. The interactive questions and the confidence score are dropped, because no stakeholder can answer inside a run.
- **Stage 2 uses the `ARCHITECTURE.md` of assignment 2**, trimmed to the component table, the ADR decisions and the constraints (ADR-011).

## Frozen version

The code used for the recorded runs is tagged `autose-v1` (`de625a2`). Later tags: `autose-v1.1` (`286f876`) crash fix, `autose-v1.2` (`7ffd0cb`) reviewer order,
`autose-v1.3` (`9957591`) injection screen fixed and fail-closed, `autose-v1.4` (`116de68`) credentials redacted from messages, `autose-v1.5` (`5b00fe4`) variants keep the review rounds.
What counts as a rerun and the token budget: `experiment/protocol.md`; every attempt, including stopped and cancelled ones, is listed in `results/runs.md`.

## Rules followed

- The workflow acts only on `Ekansh0301/tinydb`, never pushes to the upstream project, and never merges.
- API keys are repository secrets. They are not in code, logs or prompts; agent commands start with an empty environment; anything logged or commented passes through `redact` (one earlier lapse is recorded in ADR-009).

## AI assistance

AI was used for coding assistance.

# Decision experiments: what each variant changes

Two decisions are tested, one from the build side and one from the review side. Everything else is held fixed:
same repository commit, same five issues, same hidden tests, same prompts of the shared parts, same gates, same budgets.

## E1: splitting the work (ADR-001)

**Question.** Does dividing stages 1 to 4 between a planner, an implementer and a tester (with different inputs and, for the
tester, a different model) produce better results than one agent doing all four in one conversation?

| | `pipeline` (the design) | `single` (variant) |
|---|---|---|
| Agents | planner (`gpt-oss-120b`), implementer (`gpt-oss-120b`), tester (`qwen3.8-27b`) | one agent (`gpt-oss-120b`) |
| What an agent sees | per ADR-003 / ADR-011 | everything, including its own earlier reasoning |
| Who writes the tests | an agent that has not seen the implementation | the agent that wrote the code |
| Control | orchestrator state machine with the back-edges of ADR-002 | the same agent retried up to 3 times with the gate findings of the previous attempt |
| Gates | the same four gates, after each stage | the same four gates, after the single conversation |
| Budget | per stage 25 calls / 120k tokens | 70 calls / 300k tokens for the whole change |
| Stage 5 and 6 | unchanged | unchanged |

How to run: `gh workflow run autose.yml -f issue_number=<N> -f variant=single` (the pipeline runs through the label or comment).
Compared at the end of round 1 (before any review feedback): stage pass rate, hidden-test outcome, regressions, tokens, wall time.

## E2: reviewer independence (ADR-008)

**Question.** Does a reviewer from a different vendor, with its own prompt and no access to the builder's reasoning, catch more
defects and approve fewer wrong changes than the builder's own model reviewing with a fresh context?

| | `independent` (the design) | `same-model` (variant) |
|---|---|---|
| Model | `nemotron-3.5-super`, then `nemotron-3-ultra`, then `qwen3.8-27b` | `gpt-oss-120b` (the implementer's model) |
| Context | issue, diff, repository at the PR head | the same |
| Prompt, tools, permissions | the same | the same |

How to run: `gh workflow run review-seeded.yml -f pr_number=<13..17> -f issue_number=<4|6|7> -f variant=<independent|same-model> -f trial=<k>`
on the five seeded pull requests (two correct, three with a defect the included tests do not catch; labels in
`experiment/seeded_prs/labels.csv`). Three trials per cell. Measured: catch rate on the wrong ones, false rejection of the correct ones,
reviews rejected by the evidence gate, and tokens.

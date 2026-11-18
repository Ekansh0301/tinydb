# Run protocol

Fixed before the remaining runs so that results are comparable and no run is repeated just because it looked bad.

## What is frozen
The workflow code (`workflow/`, `.github/workflows/`), prompts, gates and model assignment (ADR-012) are tagged `autose-v1` before the first recorded baseline run. No change is made to them between recorded runs, except a bug in our own code (see "Reruns").

## Rehearsal (before the freeze)
The pipeline is exercised locally on every issue with `gpt-oss-20b` for the builder roles (separate daily quota from `gpt-oss-120b`). A rehearsal answers one question: does our code handle the shapes the agents produce (gates, formats, routing, release)? Failures that come from a small model's quality are not acted on. Rehearsal runs are development runs: they are not results and are not counted in `results.csv`, but their token use is added to the token total.

## Recorded runs
- One run per issue and variant, started by label, `/autose` comment or `workflow_dispatch`, in the order: #7 round 2, #4, #6, #5, #8.
- Every attempt, including stopped or cancelled ones, is listed in `results/runs.md` with a note.
- The result of an issue is its first complete attempt on frozen code: the pull request after round 1 (before review feedback) and the final pull request after the review rounds. Both are scored against the hidden tests.

## Reruns
- **Rerun**: the attempt ended for a reason outside the agents' work: quota or rate limit, endpoint timeout, a GitHub outage, or a bug in our code. A bug fix unfreezes the code; it is made on a branch, recorded in an ADR amendment, and the affected runs are repeated on the new commit. The earlier attempt stays in `runs.md`.
- **Keep as the result**: the attempt ended because a model could not do the stage within its budget (for example three failed attempts of a stage). That is a measurement of the system, not a fault.

## Experiments
- **E1 (ADR-001): split pipeline versus one agent.** Issues #4, #6 and #7. Same frozen code, same gates, same hidden tests; the single agent has one budget of 200,000 tokens for all attempts. Compared after round 1.
- **E2 (ADR-008): independent reviewer versus same-model reviewer.** The five seeded pull requests; independent: three trials with the final reviewer; same-model (`gpt-oss-120b`): two trials. Only reviews made by the final reviewer code are compared.

## Token budget (Groq `gpt-oss-120b`, six keys, 200,000 tokens per key and day)
Planned: baseline about 700,000, E1 about 600,000, E2 same-model about 500,000. Runs are spaced so that no day exceeds about 1.2 million tokens.

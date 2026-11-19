# Sequence view

A real run, from the trigger to the review and the next round: issue #6 (`startswith` / `endswith`), Actions runs
[44389251586](https://github.com/Ekansh0301/tinydb/actions/runs/44389251586) (round 1) and
[44390507790](https://github.com/Ekansh0301/tinydb/actions/runs/44390507790) (round 2). Times are from `stages.jsonl` and the job records.
The planned sequence that was committed before any agent code is in the git history of this file.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant G as gate
    participant B as build (orchestrator)
    participant P as Planner
    participant I as Implementer
    participant T as Tester
    participant C as ci
    participant R as Reviewer (separate job)
    participant N as next

    M->>G: dispatch for issue 6 (20:16)
    G->>B: sanitised issue
    B->>P: issue
    P-->>B: spec.md (gate 1 pass, 20:16)
    B->>P: spec
    P-->>B: design.md (gate 2 pass, 20:17)
    B->>I: spec, design
    I-->>B: edits (gate 3 pass, 20:21)
    B->>T: spec, file list
    T-->>B: 5 tests, suite passes (gate 4 pass, 20:22)
    B->>C: push branch, open PR
    C-->>R: CI green (20:22)
    Note over R: issue text, diff, repository at the PR head only
    R->>N: REQUEST_CHANGES (code): dead code after endswith (20:23)
    N->>G: workflow_dispatch, round 2, from stage 3
    G->>B: round 2
    B->>I: spec, design, the finding
    I-->>B: edits (gate 3 pass)
    B->>T: spec, file list
    T-->>B: tests pass, PR updated (20:24)
    C-->>R: CI green
    R->>N: APPROVE (20:25), comment on the PR, run ends
```

## Agents, artifacts and checks for each stage
See `stage_map.md`.

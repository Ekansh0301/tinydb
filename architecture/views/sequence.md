# Sequence view

Status: PLANNED. This is the intended message flow, committed before any agent code. It is replaced by a sequence taken from a real run (with Actions run links) once a run exists; the planned version stays in git history.

```mermaid
sequenceDiagram
    actor M as Maintainer
    participant GH as GitHub (issue / events)
    participant G as Job gate
    participant B as Job build (orchestrator)
    participant P as Planner
    participant I as Implementer
    participant T as Tester
    participant C as Job ci
    participant R as Job review (reviewer)
    participant N as Job next

    M->>GH: add label "autose" (or comment /autose)
    GH->>G: issues.labeled event
    G->>G: caller has write access? no other run for this issue?
    G->>G: prompt-guard score of issue text
    G->>B: sanitised issue, round=1, from_stage=1
    B->>P: issue + ARCHITECTURE.md
    P-->>B: spec.md
    B->>B: gate 1 (criteria testable)
    B->>P: spec.md + repo
    P-->>B: design.md
    B->>B: gate 2 (files and functions exist)
    B->>I: spec.md + design.md
    I-->>B: edits on autose/issue-N
    B->>B: gate 3 (diff scope, builds) -> diff.patch
    B->>T: spec.md + file list
    T-->>B: tests/ + results
    B->>B: gate 4 (new tests fail on base, pass on head, suite green)
    Note over B,I: gate 4 fails: back to Implementer, at most 2 retries
    B->>GH: push branch, open PR (pr.md)
    GH->>C: workflow_call on PR head
    C-->>B: CI green
    B->>R: trigger job review (issue, diff.patch, repo at PR head only)
    R-->>GH: review comment, review.md, verdict
    R->>N: verdict
    alt REQUEST_CHANGES and round < 2
        N->>G: workflow_dispatch round+1, from_stage = 2 (approach) or 3 (code)
    else APPROVE or round = 2
        N->>M: PR ready for human decision
    end
```

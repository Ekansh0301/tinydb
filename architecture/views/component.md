# Component view

Status: design, committed before any agent code. Updated if a decision is superseded.

Three LLM agents and one deterministic orchestrator. The orchestrator is ordinary Python; it runs the gates, owns the state machine and decides every back-edge. Release (stage 5) has no agent: it is code.

```mermaid
flowchart LR
    subgraph GH[GitHub]
        EV[/"issues: labeled<br/>issue_comment: /autose"/]
        ISS[(Issue)]
        PR[(Pull request)]
        RUNS[(branch autose-runs<br/>artifacts + state.json)]
        CODE[(branch autose/issue-N)]
    end

    EV --> GATE

    subgraph J1[job 1: gate - read only]
        GATE[authorize caller<br/>concurrency check<br/>prompt-injection screen]
    end

    subgraph J2[job 2: build - contents:write, no review rights]
        ORCH{{Orchestrator<br/>state machine, gates, budgets}}
        PLAN[Planner agent<br/>stages 1-2]
        IMPL[Implementer agent<br/>stage 3]
        TEST[Tester agent<br/>stage 4]
        REL[Release step<br/>stage 5, no LLM]
        ORCH --> PLAN
        ORCH --> IMPL
        ORCH --> TEST
        ORCH --> REL
    end

    subgraph J3[job 3: ci - reusable workflow, no secrets]
        CI[pytest on PR head]
    end

    subgraph J4[job 4: review - contents:read, pull-requests:write comment only]
        REV[Reviewer agent<br/>stage 6, own model, own prompt]
    end

    subgraph J5[job 5: next - actions:write]
        NEXT[Decide: done / re-dispatch round+1]
    end

    GATE -->|sanitised issue| ORCH
    PLAN -- "read-only repo tools" --> CODE
    IMPL -- "read, grep, edit, run build" --> CODE
    TEST -- "read, write tests/, run pytest" --> CODE
    ORCH -- "commit artifacts" --> RUNS
    REL -- "push branch, open PR" --> PR
    PR --> CI
    CI --> REV
    ISS -. "issue text only" .-> REV
    CODE -. "repo at PR head" .-> REV
    REV -- "review.md + verdict" --> RUNS
    REV -- "review comment" --> PR
    REV --> NEXT
    NEXT -- "workflow_dispatch: round+1, from_stage" --> GATE
    NEXT -- "approved or rounds used" --> HUMAN([Human: merge or close])

    subgraph LLM[model endpoints]
        GROQ[Groq: gpt-oss-120b<br/>qwen3.8-27b<br/>prompt-guard-2-86m]
        NV[NVIDIA: nemotron-3.5-super<br/>nemotron-3-ultra]
    end
    PLAN & IMPL & TEST --> GROQ
    GATE --> GROQ
    REV --> NV
    REV -. "fallback" .-> GROQ
```

## Who can see and do what

| Component | Reads | Writes | Model |
|---|---|---|---|
| Gate | event payload, collaborator permission | nothing | prompt-guard-2-86m (classifier only) |
| Orchestrator | every artifact, state.json, gate results | artifacts and state on `autose-runs`, branch `autose/issue-N` | none |
| Planner | sanitised issue, `ARCHITECTURE.md`, repo (read-only tools) | `spec.md`, `design.md` | gpt-oss-120b |
| Implementer | `spec.md`, `design.md`, repo | code on branch `autose/issue-N` | gpt-oss-120b |
| Tester | `spec.md`, file list from `design.md`, repo | files under `tests/`, `test_report.md` | gpt-oss-120b |
| Release | all artifacts | push branch, open PR, `pr.md` | none |
| Reviewer | issue text, `diff.patch`, repo at PR head | `review.md`, a PR review comment | nemotron-3.5-super, then nemotron-3-ultra, then qwen3.8-27b |

The reviewer never receives the planner's, implementer's or tester's messages, nor `spec.md`, `design.md` or `test_report.md`. See ADR-003 and ADR-008.

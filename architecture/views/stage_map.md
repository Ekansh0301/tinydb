# Stage map

Who does each stage, what it leaves behind, and what must be true before the next stage starts. A gate is decided by code, not by an agent saying "done" (ADR-007 will record the final choice once the checks are implemented).

| # | Stage | Agent | Artifact | Gate (decided by) | On failure |
|---|---|---|---|---|---|
| 1 | Requirements | Planner (A1 skill, non-interactive) | `spec.md` | Parser finds at least one acceptance criterion; every criterion has a Given/When/Then form with a checkable outcome; no criterion contains an unresolved placeholder. Code checks structure, a second short model call flags non-testable wording. | retry stage 1 once; then stop, explain in `spec.md` |
| 2 | Design | Planner (uses `ARCHITECTURE.md`) | `design.md` | Every file path named exists in the repo; every function named exists or is marked NEW; the plan covers each acceptance criterion id. Code check. | retry once; then stop |
| 3 | Implementation | Implementer | `diff.patch` | Diff is non-empty, touches only paths named in `design.md` (plus tests), package imports and `python -m compileall` succeed. Code check. | retry within budget; then stop |
| 4 | Testing | Tester | `test_report.md` | One new test per acceptance criterion id, new tests fail on the base commit and pass with the diff, full suite passes. Code check. | failing tests: back to 3 (budget 2); same criterion fails twice: back to 2 |
| 5 | Release | none (code) | `pr.md` + PR link | PR is open and the reusable CI workflow succeeded on its head commit. | stop, report CI log |
| 6 | Review | Reviewer | `review.md` | Structured verdict present with evidence for every claim; verdict is APPROVE, or round count is 2. | `approach` issue: back to 2; `code` issue: back to 3; at most 2 rounds |

After stage 6 the run ends. A person decides to merge or close. The workflow has no merge step and no token that could merge.

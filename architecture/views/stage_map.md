# Stage map

Who does each stage, what it leaves behind, and what must be true before the next stage starts. A gate is decided by code, not by an agent saying "done" (ADR-007). Models: planner and implementer `gpt-oss-120b`, tester `gpt-oss-20b`, reviewer Nemotron (ADR-012).

| # | Stage | Agent | Artifact | Gate (decided by) | On failure |
|---|---|---|---|---|---|
| 1 | Requirements | Planner (A1 skill, non-interactive) | `spec.md` | Parser finds at least one acceptance criterion; every criterion has a Given/When/Then form with a checkable outcome; no criterion contains an unresolved placeholder. Code checks structure, a second short model call flags non-testable wording. | up to 3 attempts; then stop, reason written into `spec.md` |
| 2 | Design | Planner (uses `ARCHITECTURE.md`) | `design.md` | Every file path named exists in the repo; every function named exists or is marked NEW; the plan covers each acceptance criterion id. Code check. | up to 3 attempts; then stop |
| 3 | Implementation | Implementer | `diff.patch` | Diff is non-empty, touches only paths named in `design.md` (plus tests), package imports and `python -m compileall` succeed. Code check. | up to 3 attempts in all; then stop |
| 4 | Testing | Tester | `test_report.md` | One new test per acceptance criterion id, new tests fail on the base commit and pass with the diff, full suite passes. Code check. | failing existing or new tests: back to 3 (3 attempts in all); the same criterion failing twice: back to 1, once per round; a test file that cannot be collected or lacks a test per criterion: back to the tester (3 attempts) |
| 5 | Release | none (code) | `pr.md` + PR link | PR is open and the reusable CI workflow succeeded on its head commit. | stop, report CI log |
| 6 | Review | Reviewer | `review.md` | Structured verdict present with evidence for every claim; verdict is APPROVE, or two fix cycles are used. | `approach` issue: back to 2; `code` issue: back to 3; at most 2 fix cycles (so up to 3 reviews) |

After stage 6 the run ends. A person decides to merge or close. The workflow has no merge step and no token that could merge.

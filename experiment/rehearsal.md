# Rehearsal before the freeze

Development runs of the workflow code on all four not-yet-run issues, locally, with `gpt-oss-20b` as planner, implementer and tester (a separate Groq quota from `gpt-oss-120b`) and the real reviewer on NVIDIA. Purpose: find bugs in our own code before spending recorded runs (`experiment/protocol.md`). These runs are not results and are not in `results.csv`; their tokens are part of the token total.

| GitHub issue | Outcome on `gpt-oss-20b` | Tokens | What it showed about our code |
|---|---|---|---|
| #4 (None in comparisons) | stopped at stage 2: acceptance criterion AC-5 (equality must stay unchanged) had no row in the design | 129k | The planner left out a criterion that needs no code change. The design prompt now says such a criterion still gets a row (`no change`). |
| #6 (startswith / endswith) | all stages passed, reviewer approved, 5 of 5 hidden tests | 107k | The path from issue to review works end to end. |
| #5 (search results alias the cache) | stopped at stage 4: run token budget exhausted after three failed implementations and one return to requirements | 438k | The run kept retrying after its budget was gone (three identical records). A spent run budget now stops the run at once. The design said no existing test was affected although one encodes the old behaviour, which is the trap this issue contains. |
| #8 (vague) | stopped at stage 1: a requirement without a criterion, three times, after one return from stage 4 | 251k | The gates behaved as designed; the vague issue is the hardest for a small model. |

Nothing was tuned to the small model's quality: the two code changes (design prompt wording, stopping on a spent budget) are about our own contract with the agents.

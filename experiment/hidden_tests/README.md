# Hidden acceptance tests

Four tests per issue (the assignment allows two to four), 20 in all. Written before any run, validated against a reference fix (all fail on the base commit except regression guards, all pass on the fix), and kept outside this repository until the last recorded run; they are added now. No agent could read them: the agent tools refuse the `experiment/` folder.

| File | GitHub issue | Hidden tests |
|---|---|---|
| `test_I1_none_comparison.py` | #4 | 4 |
| `test_I2_search_results_isolated.py` | #5 | 4 |
| `test_I3_startswith_endswith.py` | #6 | 4 |
| `test_I4_search_limit.py` | #7 | 4 |
| `test_I5_cond_and_ids.py` | #8 | 4 |

Run with `python experiment/score.py --issue <1..5> --branch <branch>` (it copies the tests beside, not into, the checkout and also runs the 228 baseline tests). Issue #5's natural fix conflicts with the existing test `test_query_cache_documents_are_shared_with_cache`, which encodes the old behaviour; issue #8 is vague on purpose and its tests accept either of two readings (reject the combination, or restrict it to the intersection).

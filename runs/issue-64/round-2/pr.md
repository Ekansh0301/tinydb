Refs #64 (round 2)

## Acceptance criteria
- AC-1: Given a table with any number of documents, when calling `db.search(where('type') == 'log', limit=5)`, then the returned list length shall be ≤ 5 and each element shall be a `Document`.
- AC-2: Given a table containing documents `[d1, d2, d3, d4, d5, d6]` in that storage order, when calling `db.search(where('type') == 'log', limit=3)`, then the returned list shall be `[d1, d2, d3]`.
- AC-3: Given a table with 8 matching documents, when calling `db.search(where('type') == 'log')` (no `limit` argument), then the returned list shall contain exactly 8 documents, identical to the current implementation’s result.
- AC-4: Given a named table `my_table` with 12 matching documents, when calling `db.table('my_table').search(where('type') == 'log', limit=4)`, then the returned list shall contain exactly 4 documents in the storage order of `my_table`.

## Changes
```
tests/test_autose_search.py | 43 +++++++++++++++++++++++++++++++++++++++++++
 tinydb/table.py             | 10 +++++++---
 2 files changed, 50 insertions(+), 3 deletions(-)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_limit_returns_at_most_limit, test_ac2_order_preserved, test_ac3_no_limit_returns_all, test_ac4_named_table_limit

- Failing on the base commit (expected for new behaviour): tests/test_autose_search.py::test_ac1_limit_returns_at_most_limit[json], tests/test_autose_search.py::test_ac1_limit_returns_at_most_limit[memory], tests/test_autose_search.py::test_ac2_order_preserved[json], tests/test_autose_search.py::test_ac2_order_preserved[memory], tests/test_autose_search.py::test_ac4_named_table_limit[json], tests/test_autose_search.py::test_ac4_named_table_limit[memory]
- Tests passing on the new code: 236
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-64/round-2). Tokens used so far: 53142.

Opened by the autose workflow. It never merges; a person decides.


## Stopped
Stage 5 could not pass its check: git -c http.https://github.com/.extraheader=AUTHORIZATION: basic <redacted>

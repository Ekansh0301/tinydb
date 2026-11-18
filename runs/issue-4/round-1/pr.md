Refs #4 (round 1)

## Acceptance criteria
- AC-1: Given a table containing documents `{'price': None}`, `{'price': 10}`, and `{'price': 30}`, when `db.search(where('price') < 20)` is executed, then the result list contains only the document `{'price': 10}` and no exception is raised.
- AC-2: Given a table containing documents `{'price': 'free'}`, `{'price': 5}`, and `{'price': 25}`, when `db.search(where('price') >= 10)` is executed, then the result list contains only the document `{'price': 25}` and no exception is raised.
- AC-3: Given a table containing documents `{'cost': 15}` (no `price` key) and `{'price': 12}`, when `db.search(where('price') < 20)` is executed, then the result list contains only the document `{'price': 12}` and no exception is raised.
- AC-4: Given a table with insertion order `[doc1, doc2, doc3]` where all three satisfy `where('price') < 100`, when `db.search(where('price') < 100)` is executed, then the result list order is `[doc1, doc2, doc3]`.

## Changes
```
tests/test_autose_comparison.py | 52 +++++++++++++++++++++++++++++++++++++++++
 tinydb/queries.py               | 20 ++++++++++++----
 2 files changed, 68 insertions(+), 4 deletions(-)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_none_skipped, test_ac2_non_comparable_skipped, test_ac3_missing_key_skipped, test_ac4_order_preserved

- Failing on the base commit (expected for new behaviour): tests/test_autose_comparison.py::test_ac1_none_skipped, tests/test_autose_comparison.py::test_ac2_non_comparable_skipped
- Tests passing on the new code: 232
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-4/round-1). Tokens used so far: 160447.

Opened by the autose workflow. It never merges; a person decides.

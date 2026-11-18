Refs #7 (round 2)

## Acceptance criteria
- AC-1: Given a table containing 20 documents where 15 match the condition `where('type') == 'log'`, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list shall contain exactly 10 documents, each of which satisfies the condition, and the documents shall appear in the same order as they are stored in the table.
- AC-2: Given a table containing 5 documents that all match the condition, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list shall contain all 5 matching documents (i.e., fewer than the limit) in storage order.
- AC-3: Given a table with any number of matching documents, when `db.search(where('type') == 'log')` is called (no `limit` argument), then the returned list shall contain all matching documents, identical to the current behaviour.
- AC-4: Given a named table `logs` with 30 matching documents, when `db.table('logs').search(where('type') == 'log', limit=5)` is called, then the returned list shall contain exactly 5 documents from the `logs` table in storage order.

## Changes
```
tests/test_autose_limit.py | 55 ++++++++++++++++++++++++++++++++++++++++++++++
 tinydb/table.py            | 12 +++++++++-
 2 files changed, 66 insertions(+), 1 deletion(-)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_limit_returns_exactly_limit, test_ac2_limit_fewer_than_limit, test_ac3_no_limit_returns_all, test_ac4_named_table_limit

- Failing on the base commit (expected for new behaviour): tests/test_autose_limit.py::test_ac1_limit_returns_exactly_limit, tests/test_autose_limit.py::test_ac2_limit_fewer_than_limit, tests/test_autose_limit.py::test_ac4_named_table_limit
- Tests passing on the new code: 232
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-7/round-2). Tokens used so far: 23821.

Opened by the autose workflow. It never merges; a person decides.

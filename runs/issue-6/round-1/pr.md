Refs #6 (round 1)

## Acceptance criteria
- AC-1: Given a collection containing documents `{'name': 'Alice'}` and `{'name': 'Bob'}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}`.
- AC-2: Given a collection containing documents `{'name': 'Jackson'}` and `{'name': 'John'}`, when `db.search(where('name').endswith('son'))` is executed, then the result set shall contain only the document `{'name': 'Jackson'}`.
- AC-3: Given a collection containing documents `{'name': 'Alice'}`, `{}` (field missing), `{'name': None}`, and `{'name': 123}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}` and no exception shall be raised.
- AC-4: Given a collection containing documents `{'name': 'Alice'}`, `{}` (field missing), `{'name': None}`, and `{'name': 123}`, when `db.search(where('name').endswith('ice'))` is executed, then the result set shall contain only the document `{'name': 'Alice'}` and no exception shall be raised.
- AC-5: Given a collection containing documents `{'name': 'alice'}` and `{'name': 'Alice'}`, when `db.search(where('name').startswith('Al'))` is executed, then the result set shall contain only `{'name': 'Alice'}` (case-sensitive match).

## Changes
```
tests/test_autose_strings.py | 59 ++++++++++++++++++++++++++++++++++++++++++++
 tinydb/queries.py            | 43 ++++++++++++++++++++++++++++++++
 2 files changed, 102 insertions(+)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_startswith_basic, test_ac2_endswith_basic, test_ac3_nonstring_startswith, test_ac4_nonstring_endswith, test_ac5_case_sensitive

- Failing on the base commit (expected for new behaviour): tests/test_autose_strings.py::test_ac1_startswith_basic, tests/test_autose_strings.py::test_ac2_endswith_basic, tests/test_autose_strings.py::test_ac3_nonstring_startswith, tests/test_autose_strings.py::test_ac4_nonstring_endswith, tests/test_autose_strings.py::test_ac5_case_sensitive
- Tests passing on the new code: 233
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-6/round-1). Tokens used so far: 120598.

Opened by the autose workflow. It never merges; a person decides.

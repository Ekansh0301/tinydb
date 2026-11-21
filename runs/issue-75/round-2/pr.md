Refs #75 (round 2)

## Acceptance criteria
- AC-1: Given a collection with documents `[{ "name": "Jackson" }, { "name": "Emily" }]`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall contain only the document `{"name": "Jackson"}`.
- AC-2: Given a document `{"name": "Jackson"}`, when `db.search(where('name').contains_text('SON'))` is executed, then the result set shall be empty, confirming case-sensitivity.
- AC-3: Given a collection with documents `[{ "age": 30 }, { "name": null }, { }]`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall be empty and no exception shall be raised.
- AC-4: Given a document `{"name": "sonic"}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall contain that document.
- AC-5: Given a collection with documents `[{ "name": "Jackson", "active": true }, { "name": "Jackson", "active": false }]`, when `db.search(where('name').contains_text('son').and(where('active').equals(True)))` is executed, then the result set shall contain only the first document, demonstrating composability.

## Changes
```
tests/test_autose_contains_text.py | 50 ++++++++++++++++++++++++++++++++++++++
 tinydb/queries.py                  | 17 ++++++++++++-
 2 files changed, 66 insertions(+), 1 deletion(-)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_contains_text_basic, test_ac2_contains_text_case_sensitive, test_ac3_contains_text_non_string, test_ac4_contains_text_substring, test_ac5_contains_text_composable

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_contains_text_basic, tests/test_autose_contains_text.py::test_ac2_contains_text_case_sensitive, tests/test_autose_contains_text.py::test_ac3_contains_text_non_string, tests/test_autose_contains_text.py::test_ac4_contains_text_substring, tests/test_autose_contains_text.py::test_ac5_contains_text_composable
- Tests passing on the new code: 233
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-75/round-2). Tokens used so far: 154180.

Opened by the autose workflow. It never merges; a person decides.

Refs #73 (round 2)

## Acceptance criteria
- AC-1: Given a collection containing a document `{'name': 'Jackson'}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall include that document.
- AC-2: Given a collection containing a document `{'name': 'Jackson'}`, when `db.search(where('name').contains_text('Son'))` is executed, then the result set shall **not** include that document (case-sensitive).
- AC-3: Given a collection containing a document `{'age': 30}` (field missing), when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.
- AC-4: Given a collection containing a document `{'name': None}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.
- AC-5: Given a collection containing a document `{'name': 12345}`, when `db.search(where('name').contains_text('son'))` is executed, then the result set shall not include that document and no exception shall be thrown.

## Changes
```
tests/test_autose_contains_text.py | 45 ++++++++++++++++++++++++++++++++++++++
 tinydb/queries.py                  | 15 ++++++++++++-
 2 files changed, 59 insertions(+), 1 deletion(-)
```

## Tests
# Test report

Result: **PASS**

New tests: test_ac1_contains_text_matches, test_ac2_contains_text_case_sensitive, test_ac3_missing_field_no_match, test_ac4_none_value_no_match, test_ac5_non_string_no_match

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_contains_text_matches, tests/test_autose_contains_text.py::test_ac2_contains_text_case_sensitive, tests/test_autose_contains_text.py::test_ac3_missing_field_no_match, tests/test_autose_contains_text.py::test_ac4_none_value_no_match, tests/test_autose_contains_text.py::test_ac5_non_string_no_match
- Tests passing on the new code: 233
- Failing on the new code: none

## Process
Spec, design, test report and review are in [autose-runs](https://github.com/Ekansh0301/tinydb/tree/autose-runs/runs/issue-73/round-2). Tokens used so far: 41155.

Opened by the autose workflow. It never merges; a person decides.

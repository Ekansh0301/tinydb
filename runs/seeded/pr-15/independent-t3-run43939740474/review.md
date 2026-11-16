# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to the `Query` class in `tinydb/queries.py`. Both use `_generate_test` with a lambda that checks `isinstance(value, str)` before calling the string method, so missing fields, `None`, and numbers never match and never raise. Case-sensitive matching is preserved. New tests in `tests/test_startswith_seed.py` cover basic matching and non-string non-matching. All 234 tests pass and a manual snippet confirms edge cases (missing field, None, number, case sensitivity) behave as required by the issue.

## Checks
- [pass] startswith/endswith match only strings and skip non-strings without error: tests/test_startswith_seed.py::test_non_strings_do_not_match passed; full suite 234 passed
- [pass] case-sensitive matching works: snippet: startswith('Al') returns ['Alice','Alan'] but not 'alice'; startswith('al') returns ['alice']
- [pass] missing field, None, number do not match: snippet: db with {'name': 5}, {'name': None}, {'x': 1} returns only string matches; no exception raised

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

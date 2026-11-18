# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to `Query` in `tinydb/queries.py`, each using `_generate_test` with a lambda that checks `isinstance(value, str)` before calling the string method, so missing fields, `None`, and numbers never match and never raise. The new test file covers basic matching and non-string exclusion. Full test suite passes and my own snippet confirms edge cases (empty prefix matches all strings, missing field returns no results, no errors).

## Checks
- [pass] startswith/endswith match only strings and skip non-strings without error: python -m pytest tests/test_startswith_seed.py -v → 6 passed
- [pass] full test suite still passes: python -m pytest tests/ -q → all tests passed
- [pass] edge cases: missing field, None, number, empty prefix behave correctly: snippet: startswith 'Al' → ['Alice']; endswith 'ce' → ['Alice']; startswith '' → ['Alice', '']; missing field → [] with no error

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

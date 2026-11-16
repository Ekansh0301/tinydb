# Review

Verdict: **APPROVE**

Adds startswith/endswith methods to Query in tinydb/queries.py. They use _generate_test which safely handles missing fields and non-string values, and the lambda guards with isinstance(value, str). All 6 new tests pass and the full suite passes. Manual edge-case checks confirm no errors for None, numbers, missing fields, or empty prefix/suffix.

## Checks
- [pass] startswith and endswith match only string values: tests/test_startswith_seed.py test_non_strings_do_not_match passes; manual snippet confirms None/5/missing field don't match
- [pass] missing fields and non-strings produce no error: _generate_test runner catches KeyError/TypeError returning False (tinydb/queries.py:235-247); manual snippet with None, 5, missing field runs cleanly
- [pass] full existing test suite still passes: python -m pytest tests/ -q exits 0

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

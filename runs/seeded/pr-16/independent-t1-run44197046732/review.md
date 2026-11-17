# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to the `Query` class in `tinydb/queries.py`. Both use `_generate_test` with a lambda that guards with `isinstance(value, str)`, so missing fields, `None`, and numbers never match and never raise. Case-sensitive matching is provided by Python's `str.startswith`/`str.endswith`. New tests in `tests/test_startswith_seed.py` cover startswith, endswith, and non-string non-matching behavior.

## Checks
- [pass] All tests pass including new startswith/endswith tests: python -m pytest tests/ -q → exit code 0, 62 passed
- [pass] Non-string values (missing field, None, number, empty string) do not match without error: python -c snippet with TinyDB(':memory:') → startswith Al returns ['Alice','Al'], endswith ce returns ['Alice'], missing field and empty string excluded

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to the `Query` class in `tinydb/queries.py`, using `_generate_test` with a lambda that checks `isinstance(value, str)` before calling `str.startswith`/`str.endswith`. This satisfies the issue: only strings match, missing/None/number fields don't match (no error), and matching is case-sensitive. New tests in `tests/test_startswith_seed.py` cover both methods and non-string handling. All 234 tests pass, and my own edge-case snippet confirms correct behavior for case sensitivity, empty prefix/suffix, and non-string values.

## Checks
- [pass] startswith/endswith match only strings and skip non-strings without error: python -m pytest tests/test_startswith_seed.py -v → 6 passed; snippet shows startswith('A') returns only ['Alice','Alan'] skipping 5, None, missing field
- [pass] no regressions in existing test suite: python -m pytest tests/ -v → 234 passed
- [pass] case-sensitive matching works: snippet: startswith('Al') matches Alice/Alan but not alice; startswith('al') matches only alice

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

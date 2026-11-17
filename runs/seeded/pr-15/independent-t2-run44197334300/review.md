# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to `Query` in `tinydb/queries.py`, each using `_generate_test` with a lambda that guards with `isinstance(value, str)` before calling the string method. This satisfies the issue: only strings match, missing/`None`/number fields don't match and don't error, and matching is case-sensitive. New tests in `tests/test_startswith_seed.py` cover both methods plus non-string handling, and the full existing test suite passes.

## Checks
- [pass] startswith/endswith match only string values and skip non-strings without error: tests/test_startswith_seed.py lines 14-16 pass; snippet confirmed missing field, None, int, and empty-string cases behave correctly
- [pass] full existing test suite still passes: `python -m pytest tests/` exit code 0, all tests collected and passed

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

# Review

Verdict: **APPROVE**

Added `startswith` and `endswith` methods to `Query` in `tinydb/queries.py`, each generating a test that checks `isinstance(value, str)` before calling the string method, so missing fields, `None`, and numbers never match and never raise. Case-sensitive matching as requested. New tests in `tests/test_startswith_seed.py` cover both methods and the non-string edge case; all pass, and the full test suite passes. A manual snippet confirmed missing/None/number fields produce no matches and no errors, and case-sensitivity works.

## Checks
- [pass] startswith/endswith match only strings and ignore non-strings without error: python -m pytest tests/test_startswith_seed.py -v → 6 passed; full suite → 100% pass
- [pass] edge cases: missing field, None, number do not match; case-sensitive: snippet with MemoryStorage: startswith('Al') → ['Alice','Alan'], endswith('ce') → ['Alice'], startswith('al') → []

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

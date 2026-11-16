# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The issue asks that `<`, `>`, `<=`, `>=` all skip documents where the field is `None` (or otherwise incomparable). The diff only patches `__lt__`; `__le__`, `__gt__`, and `__ge__` still raise TypeError on `None`. I confirmed `<=` still crashes with a live snippet, so the fix is incomplete.

## Checks
- [pass] where('a') < 3 skips None and missing-key docs: python -c snippet using MemoryStorage: lt returned [1], no crash
- [fail] where('a') <= 3 still crashes on None: same snippet: TypeError '<=' not supported between instances of 'NoneType' and 'int' at queries.py:302

## Findings
- (high) tinydb/queries.py:302 __le__ lambda lacks the `value is not None` guard, so <= crashes on None.
- (high) tinydb/queries.py:315 __gt__ lambda lacks the guard, so > crashes on None.
- (high) tinydb/queries.py:328 __ge__ lambda lacks the guard, so >= crashes on None.
- (medium) tests/test_none_seed.py:5 New test only covers `<`; should cover all four operators and mixed string/number fields per the issue.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

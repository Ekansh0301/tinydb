# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The fix guards against None for `<` only, but the issue reports `<`, `>`, `<=`, and `>=` all crash. Running the code confirms `<=`, `>`, and `>=` still raise TypeError on None values, and the added test only covers `<`. The approach is right but the implementation is incomplete.

## Checks
- [pass] `<` skips None after the fix: python -c snippet: db.search(where('a') < 3) returns [1], no crash
- [fail] `<=`, `>`, `>=` still crash on None: python -c snippet: all three raise TypeError: '<=' not supported between instances of 'NoneType' and 'int'
- [pass] test suite passes: python -m pytest tests/ -q: exit code 0, 100% passed

## Findings
- (high) tinydb/queries.py:302 __le__ lambda lacks 'value is not None' guard, still crashes on None
- (high) tinydb/queries.py:315 __gt__ lambda lacks 'value is not None' guard, still crashes on None
- (high) tinydb/queries.py:328 __ge__ lambda lacks 'value is not None' guard, still crashes on None
- (medium) tests/test_none_seed.py:5 test only covers '<', not the other three operators mentioned in the issue

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

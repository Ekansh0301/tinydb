# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR only patches `Query.__lt__` to skip `None`, but the issue explicitly states `>`, `<=`, and `>=` (and mixed str/num) crash the same way. Those three operators still raise TypeError on `None`, so the fix is incomplete. All 230 existing tests pass and the new `<` test passes, but the remaining operators need the same `value is not None and` guard.

## Checks
- [pass] where('a') < 3 skips None and missing key: snippet: [d['a'] for d in db.search(where('a') < 3)] == [1]; tests/test_none_seed.py passes
- [fail] where('a') <= 5 crashes on None: snippet raised TypeError: '<=' not supported between instances of 'NoneType' and 'int' at tinydb/queries.py:302
- [fail] where('a') > 3 crashes on None: snippet would hit tinydb/queries.py:315 lambda value: value > rhs with no None guard
- [fail] where('a') >= 1 crashes on None: snippet would hit tinydb/queries.py:328 lambda value: value >= rhs with no None guard

## Findings
- (high) tinydb/queries.py:302 __le__ lacks a None guard; crashes on None values
- (high) tinydb/queries.py:315 __gt__ lacks a None guard; crashes on None values
- (high) tinydb/queries.py:328 __ge__ lacks a None guard; crashes on None values

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

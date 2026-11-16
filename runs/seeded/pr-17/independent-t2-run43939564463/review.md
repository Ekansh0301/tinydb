# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR only guards `__lt__` (`<`) against None, but the issue reports that `>`, `<=`, and `>=` crash identically. I confirmed `<` now skips None while `<=`, `>`, `>=` still raise TypeError on None values. The fix needs to be applied to all four comparison operators.

## Checks
- [pass] where('a') < 3 skips None and missing keys: python -c snippet: db.search(where('a') < 3) returned [1] without error
- [fail] where('a') <= 3 still crashes on None: python -c snippet: TypeError: '<=' not supported between instances of 'NoneType' and 'int'
- [fail] where('a') > 3 still crashes on None: python -c snippet: TypeError: '>' not supported between instances of 'NoneType' and 'int'
- [fail] where('a') >= 3 still crashes on None: python -c snippet: TypeError: '>=' not supported between instances of 'NoneType' and 'int'

## Findings
- (high) tinydb/queries.py:302 __le__ lambda lacks None guard, crashes on None values
- (high) tinydb/queries.py:315 __gt__ lambda lacks None guard, crashes on None values
- (high) tinydb/queries.py:328 __ge__ lambda lacks None guard, crashes on None values

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

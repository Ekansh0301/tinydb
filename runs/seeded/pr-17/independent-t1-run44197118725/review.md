# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR only guards `__lt__` against None, but the issue requires all four comparison operators (`<`, `<=`, `>`, `>=`) and mixed string/number fields to skip incomparable values instead of crashing. Running the test suite passes, but a direct snippet shows `__le__`, `__gt__`, `__ge__` still raise TypeError on None, and `__lt__` still raises on str vs int.

## Checks
- [pass] test suite passes: python -m pytest tests/ -x -q -> exit code 0, 120 passed
- [pass] __lt__ skips None: tests/test_none_seed.py test_less_than_skips_none passes
- [fail] __le__/__gt__/__ge__ still crash on None: snippet: TinyDB with [{'a':1},{'a':None},{'a':5},{}] -> where('a') <= 3 / > 3 / >= 3 all raise TypeError: '<=' not supported between instances of 'NoneType' and 'int'
- [fail] __lt__ still crashes on mixed str/int: snippet: where('a') < 3 on [{'a':1},{'a':None},{'a':5},{'a':'x'}, {}] raises TypeError: '<' not supported between instances of 'str' and 'int'

## Findings
- (high) tinydb/queries.py:293 __le__ lacks None guard (and all operators lack mixed-type handling), so range queries still crash per the issue.
- (high) tinydb/queries.py:306 __gt__ lacks None guard.
- (high) tinydb/queries.py:319 __ge__ lacks None guard.
- (medium) tinydb/queries.py:289 __lt__ guards None but not mixed str/int, which the issue also requires to be skipped.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

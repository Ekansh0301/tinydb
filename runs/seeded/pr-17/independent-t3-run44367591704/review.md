# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR only fixes `__lt__` (`<`) to skip `None` values, but the issue reports that `>`, `<=`, and `>=` crash the same way. My snippet confirms `<` now works while `>`, `<=`, and `>=` still raise `TypeError` on `None` fields. The fix must be applied consistently to all four comparison operators.

## Checks
- [pass] Full test suite passes: python -m pytest -q -> exit 0, all tests pass
- [fail] Only < skips None; >, <=, >= still crash: python -c snippet: < OK [1]; > CRASH TypeError; <= CRASH TypeError; >= CRASH TypeError

## Findings
- (high) tinydb/queries.py:293 __le__ still uses `lambda value: value <= rhs` without a None guard, crashing on None fields.
- (high) tinydb/queries.py:306 __gt__ still uses `lambda value: value > rhs` without a None guard, crashing on None fields.
- (high) tinydb/queries.py:319 __ge__ still uses `lambda value: value >= rhs` without a None guard, crashing on None fields.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

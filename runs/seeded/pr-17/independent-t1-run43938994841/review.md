# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The approach of guarding comparisons with `is not None` is correct, but the implementation is incomplete: only `__lt__` was patched. `__le__`, `__gt__`, and `__ge__` still raise TypeError when a field holds None (and mixed str/num fields also crash), contradicting the issue which names all four operators. The single new test only covers `<`.

## Checks
- [pass] where('a') < 3 skips None: python -c snippet: lt returned [1]; tests/test_none_seed.py passes
- [fail] where('a') <= 3 skips None: python -c snippet raised TypeError: '<=' not supported between instances of 'NoneType' and 'int' at queries.py:302
- [fail] where('a') > 3 skips None: python -c snippet raised TypeError: '>' not supported between instances of 'NoneType' and 'int' at queries.py:315
- [fail] where('a') >= 3 skips None: python -c snippet raised TypeError: '>=' not supported between instances of 'NoneType' and 'int' at queries.py:328
- [pass] full test suite passes: python -m pytest tests/ -q exit code 0

## Findings
- (high) tinydb/queries.py:302 __le__ lambda lacks the `is not None` guard, so None values still crash <= queries
- (high) tinydb/queries.py:315 __gt__ lambda lacks the `is not None` guard
- (high) tinydb/queries.py:328 __ge__ lambda lacks the `is not None` guard
- (medium) tests/test_none_seed.py:4 test only covers `<`, not `<=`, `>`, `>=`, or mixed str/num fields as the issue describes

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

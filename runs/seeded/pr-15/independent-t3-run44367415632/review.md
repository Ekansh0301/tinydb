# Review

Verdict: **APPROVE**

The PR adds `startswith` and `endswith` methods to the `Query` class in `tinydb/queries.py`, implemented via the existing `_generate_test` helper. The lambdas guard with `isinstance(value, str)` so missing fields, `None`, and numbers safely don't match without erroring. New tests in `tests/test_startswith_seed.py` cover startswith, endswith, and non-string non-matching. The full test suite passes and my own edge-case snippet confirms correct behavior.

## Checks
- [pass] startswith/endswith methods exist and match strings correctly: python -m pytest tests/test_startswith_seed.py -v → 6 passed
- [pass] non-string values (None, number, missing field) do not match and raise no error: python -c snippet: startswith('A') on [{name:5},{name:None},{x:1},{name:'Al'}] returned ['Al'] with no exception
- [pass] full existing test suite still passes: python -m pytest tests/ -q → all passed

## Findings

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

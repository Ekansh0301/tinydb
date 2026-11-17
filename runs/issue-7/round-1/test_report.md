# Test report

Result: **FAIL**

New tests: test_ac1_search_returns_list_and_no_exception, test_ac2_limit_returns_exactly_ten_and_order, test_ac3_no_limit_equals_full, test_ac4_named_table_limit, test_ac5_limit_none_is_unlimited, test_ac6_negative_limit_raises_valueerror

- Failing on the base commit (expected for new behaviour): tests/test_autose_search.py::test_ac1_search_returns_list_and_no_exception, tests/test_autose_search.py::test_ac2_limit_returns_exactly_ten_and_order, tests/test_autose_search.py::test_ac4_named_table_limit, tests/test_autose_search.py::test_ac5_limit_none_is_unlimited, tests/test_autose_search.py::test_ac6_negative_limit_raises_valueerror
- Tests passing on the new code: 232
- Failing on the new code: tests/test_autose_search.py::test_ac2_limit_returns_exactly_ten_and_order, tests/test_autose_search.py::test_ac6_negative_limit_raises_valueerror

Gate findings:
- test suite does not pass: tests/test_autose_search.py::test_ac2_limit_returns_exactly_ten_and_order, tests/test_autose_search.py::test_ac6_negative_limit_raises_valueerror

Last lines of the full suite run:
```
assert len(limited) == 10
E       AssertionError: assert 20 == 10
E        +  where 20 = len([{'type': 'log', 'id': 0}, {'type': 'log', 'id': 1}, {'type': 'log', 'id': 2}, {'type': 'log', 'id': 3}, {'type': 'log', 'id': 4}, {'type': 'log', 'id': 5}, ...])

tests/test_autose_search.py:26: AssertionError
__________________ test_ac6_negative_limit_raises_valueerror ___________________

    def test_ac6_negative_limit_raises_valueerror():
        db = make_db(3)
>       with pytest.raises(ValueError) as exc:
             ^^^^^^^^^^^^^^^^^^^^^^^^^
E       Failed: DID NOT RAISE ValueError

tests/test_autose_search.py:60: Failed
=========================== short test summary info ============================
FAILED tests/test_autose_search.py::test_ac2_limit_returns_exactly_ten_and_order
FAILED tests/test_autose_search.py::test_ac6_negative_limit_raises_valueerror
2 failed, 232 passed in 0.77s

```

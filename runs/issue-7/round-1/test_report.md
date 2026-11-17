# Test report

Result: **FAIL**

New tests: test_ac1_search_returns_list_and_no_exception, test_ac2_limit_respects_order_and_count, test_ac3_no_limit_same_as_default, test_ac4_named_table_limit, test_ac5_limit_none_unlimited, test_ac6_negative_limit_raises_valueerror

- Failing on the base commit (expected for new behaviour): tests/test_autose_search.py::test_ac1_search_returns_list_and_no_exception, tests/test_autose_search.py::test_ac2_limit_respects_order_and_count, tests/test_autose_search.py::test_ac3_no_limit_same_as_default, tests/test_autose_search.py::test_ac4_named_table_limit, tests/test_autose_search.py::test_ac5_limit_none_unlimited, tests/test_autose_search.py::test_ac6_negative_limit_raises_valueerror
- Tests passing on the new code: 233
- Failing on the new code: tests/test_autose_search.py::test_ac2_limit_respects_order_and_count

Gate findings:
- test suite does not pass: tests/test_autose_search.py::test_ac2_limit_respects_order_and_count

Last lines of the full suite run:
```
                                            [100%]
=================================== FAILURES ===================================
___________________ test_ac2_limit_respects_order_and_count ____________________

    def test_ac2_limit_respects_order_and_count():
        db = make_db(20)
        full = db.search(where('type') == 'log')
        limited = db.search(where('type') == 'log', limit=10)
>       assert len(limited) == 10
E       AssertionError: assert 20 == 10
E        +  where 20 = len([{'type': 'log', 'id': 0}, {'type': 'log', 'id': 1}, {'type': 'log', 'id': 2}, {'type': 'log', 'id': 3}, {'type': 'log', 'id': 4}, {'type': 'log', 'id': 5}, ...])

tests/test_autose_search.py:26: AssertionError
=========================== short test summary info ============================
FAILED tests/test_autose_search.py::test_ac2_limit_respects_order_and_count
1 failed, 233 passed in 0.71s

```

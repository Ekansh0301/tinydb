# Test report

Result: **FAIL**

New tests: test_ac1_limit_returns_list, test_ac2_limit_ten_documents, test_ac3_no_limit_returns_all, test_ac4_limit_on_named_table, test_ac5_nonpositive_limit, test_ac6_limit_exceeds_matches

- Failing on the base commit (expected for new behaviour): tests/test_autose_limit.py::test_ac1_limit_returns_list, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac4_limit_on_named_table, tests/test_autose_limit.py::test_ac5_nonpositive_limit[-3], tests/test_autose_limit.py::test_ac5_nonpositive_limit[0], tests/test_autose_limit.py::test_ac6_limit_exceeds_matches
- Tests passing on the new code: 226
- Failing on the new code: tests/test_autose_limit.py::test_ac1_limit_returns_list, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac4_limit_on_named_table, tests/test_autose_limit.py::test_ac5_nonpositive_limit[-3], tests/test_autose_limit.py::test_ac5_nonpositive_limit[0], tests/test_autose_limit.py::test_ac6_limit_exceeds_matches, tests/test_tinydb.py::test_query_cache, tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache

Gate findings:
- test suite does not pass: tests/test_autose_limit.py::test_ac1_limit_returns_list, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac4_limit_on_named_table, tests/test_autose_limit.py::test_ac5_nonpositive_limit[-3], tests/test_autose_limit.py::test_ac5_nonpositive_limit[0], tests/test_autose_limit.py::test_ac6_limit_exceeds_matches, tests/test_tinydb.py::test_query_cache

Last lines of the full suite run:
```
 -v to get more diff

tests/test_tinydb.py:747: AssertionError
=========================== short test summary info ============================
FAILED tests/test_autose_limit.py::test_ac1_limit_returns_list - TypeError: T...
FAILED tests/test_autose_limit.py::test_ac2_limit_ten_documents - TypeError: ...
FAILED tests/test_autose_limit.py::test_ac3_no_limit_returns_all - TypeError:...
FAILED tests/test_autose_limit.py::test_ac4_limit_on_named_table - TypeError:...
FAILED tests/test_autose_limit.py::test_ac5_nonpositive_limit[0] - TypeError:...
FAILED tests/test_autose_limit.py::test_ac5_nonpositive_limit[-3] - TypeError...
FAILED tests/test_autose_limit.py::test_ac6_limit_exceeds_matches - TypeError...
FAILED tests/test_tinydb.py::test_query_cache - AssertionError: assert [{'nam...
FAILED tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache
9 failed, 226 passed in 0.50s

```

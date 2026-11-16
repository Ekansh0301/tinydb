# Test report

Result: **FAIL**

New tests: test_ac1_returns_list_and_no_exception, test_ac2_limit_ten_documents, test_ac3_no_limit_returns_all, test_ac4_named_table_limit, test_ac5_and_ac6_nonpositive_limit_returns_empty, test_ac7_limit_larger_than_matches

- Failing on the base commit (expected for new behaviour): tests/test_autose_limit.py::test_ac1_returns_list_and_no_exception, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac4_named_table_limit, tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[-3], tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[0], tests/test_autose_limit.py::test_ac7_limit_larger_than_matches
- Tests passing on the new code: 229
- Failing on the new code: tests/test_autose_limit.py::test_ac1_returns_list_and_no_exception, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[-3], tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[0], tests/test_autose_limit.py::test_ac7_limit_larger_than_matches

Gate findings:
- no test for: AC-6
- test suite does not pass: tests/test_autose_limit.py::test_ac1_returns_list_and_no_exception, tests/test_autose_limit.py::test_ac2_limit_ten_documents, tests/test_autose_limit.py::test_ac3_no_limit_returns_all, tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[-3], tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[0], tests/test_autose_limit.py::test_ac7_limit_larger_than_matches

Last lines of the full suite run:
```
unt, table_name=None):
        if table_name:
            table = db.table(table_name)
        else:
>           table = db.table()
                    ^^^^^^^^^^
E           TypeError: TinyDB.table() missing 1 required positional argument: 'name'

tests/test_autose_limit.py:13: TypeError
=========================== short test summary info ============================
FAILED tests/test_autose_limit.py::test_ac1_returns_list_and_no_exception - T...
FAILED tests/test_autose_limit.py::test_ac2_limit_ten_documents - TypeError: ...
FAILED tests/test_autose_limit.py::test_ac3_no_limit_returns_all - TypeError:...
FAILED tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[0]
FAILED tests/test_autose_limit.py::test_ac5_and_ac6_nonpositive_limit_returns_empty[-3]
FAILED tests/test_autose_limit.py::test_ac7_limit_larger_than_matches - TypeE...
6 failed, 229 passed in 0.63s

```

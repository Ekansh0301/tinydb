# Test report

Result: **PASS**

New tests: test_ac1_limit_returns_exactly_limit, test_ac2_limit_fewer_than_limit, test_ac3_no_limit_returns_all, test_ac4_named_table_limit

- Failing on the base commit (expected for new behaviour): tests/test_autose_limit.py::test_ac1_limit_returns_exactly_limit, tests/test_autose_limit.py::test_ac2_limit_fewer_than_limit, tests/test_autose_limit.py::test_ac4_named_table_limit
- Tests passing on the new code: 232
- Failing on the new code: none

Last lines of the full suite run:
```
exit code 0
........................................................................ [ 31%]
........................................................................ [ 62%]
........................................................................ [ 93%]
................                                                         [100%]
232 passed in 0.54s

```

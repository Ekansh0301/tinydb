# Test report

Result: **PASS**

New tests: test_ac1_limit_returns_at_most_limit, test_ac2_order_preserved, test_ac3_no_limit_returns_all, test_ac4_named_table_limit

- Failing on the base commit (expected for new behaviour): tests/test_autose_search.py::test_ac1_limit_returns_at_most_limit[json], tests/test_autose_search.py::test_ac1_limit_returns_at_most_limit[memory], tests/test_autose_search.py::test_ac2_order_preserved[json], tests/test_autose_search.py::test_ac2_order_preserved[memory], tests/test_autose_search.py::test_ac4_named_table_limit[json], tests/test_autose_search.py::test_ac4_named_table_limit[memory]
- Tests passing on the new code: 236
- Failing on the new code: none

Last lines of the full suite run:
```
exit code 0
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 91%]
....................                                                     [100%]
236 passed in 0.84s

```

# Test report

Result: **FAIL**

New tests: test_ac1_limit_kwarg_accepted, test_ac2_limit_returns_first_n

- Failing on the base commit (expected for new behaviour): tests/test_autose_search_limit.py::test_ac1_limit_kwarg_accepted[json], tests/test_autose_search_limit.py::test_ac1_limit_kwarg_accepted[memory], tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[json], tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[memory]
- Tests passing on the new code: 230
- Failing on the new code: tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[json], tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[memory]

Gate findings:
- no test for: AC-3, AC-4, AC-5 (found only: test_ac1_limit_kwarg_accepted, test_ac2_limit_returns_first_n). Every test must be named test_ac<N>_<what>, with N the criterion number
- test suite does not pass: tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[json], tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[memory]

Last lines of the full suite run:
```

db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac2_limit_returns_first_n(db):
>       _
E       NameError: name '_' is not defined

tests/test_autose_search_limit.py:24: NameError
_____________________ test_ac2_limit_returns_first_n[json] _____________________

db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac2_limit_returns_first_n(db):
>       _
E       NameError: name '_' is not defined

tests/test_autose_search_limit.py:24: NameError
=========================== short test summary info ============================
FAILED tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[memory]
FAILED tests/test_autose_search_limit.py::test_ac2_limit_returns_first_n[json]
2 failed, 230 passed in 0.45s

```

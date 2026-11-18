# Test report

Result: **FAIL**

New tests: test_ac1_independent_copies, test_ac2_no_auto_persist, test_ac3_config_return_copies, test_ac4_clear_cache

- Failing on the base commit (expected for new behaviour): tests/test_autose_copy.py::test_ac1_independent_copies, tests/test_autose_copy.py::test_ac3_config_return_copies
- Tests passing on the new code: 228
- Failing on the new code: tests/test_tables.py::test_query_cache_with_mutable_callable[json], tests/test_tables.py::test_query_cache_with_mutable_callable[memory], tests/test_tinydb.py::test_lambda_query, tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache

Gate findings:
- test suite does not pass: tests/test_tables.py::test_query_cache_with_mutable_callable[json], tests/test_tables.py::test_query_cache_with_mutable_callable[memory], tests/test_tinydb.py::test_lambda_query, tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache

Last lines of the full suite run:
```
oo') == 'bar'
        query.is_cacheable = lambda: False
        assert db.search(query) == [{'foo': 'bar'}]
>       assert not db._query_cache
E       AssertionError: assert not <tinydb.utils.LRUCache object at 0x73f3d52e7ec0>
E        +  where <tinydb.utils.LRUCache object at 0x73f3d52e7ec0> = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=1, all_tables_documents_count=['_default=1']>._query_cache

tests/test_tinydb.py:839: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tables.py::test_query_cache_with_mutable_callable[memory]
FAILED tests/test_tables.py::test_query_cache_with_mutable_callable[json] - A...
FAILED tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache
FAILED tests/test_tinydb.py::test_lambda_query - AssertionError: assert not <...
4 failed, 228 passed in 0.53s

```


## Stopped
Stage 4 could not pass its check: test suite does not pass: tests/test_tables.py::test_query_cache_with_mutable_callable[json], tests/test_tables.py::test_query_cache_with_mutable_callable[memory], tests/test_tinydb.py::test_lambda_query, tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache; failing: tests/test_tables.py::test_query_cache_with_mutable_callable[json], tests/test_tables.py::test_query_cache_with_mutable_callable[memory], tests/test_tinydb.py::test_lambda_query, tests/test_tinydb.py::test_query_cache_documents_are_shared_with_cache

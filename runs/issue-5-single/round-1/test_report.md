# Test report

Result: **FAIL**

New tests: test_ac1_modified_field_not_cached, test_ac2_modified_nested_not_cached

- Failing on the base commit (expected for new behaviour): tests/test_autose_cache.py::test_ac1_modified_field_not_cached, tests/test_autose_cache.py::test_ac2_modified_nested_not_cached
- Tests passing on the new code: 229
- Failing on the new code: tests/test_autose_cache.py::test_ac2_modified_nested_not_cached

Gate findings:
- test suite does not pass: tests/test_autose_cache.py::test_ac2_modified_nested_not_cached

Last lines of the full suite run:
```
= FAILURES ===================================
_____________________ test_ac2_modified_nested_not_cached ______________________

db = <TinyDB tables=['_default'], tables_count=1, default_table_documents_count=3, all_tables_documents_count=['_default=3']>

    def test_ac2_modified_nested_not_cached(db):
        users = db.search(where('team') == 'red')
        users[0]['tags'].append('new')
        fresh = db.search(where('team') == 'red')
        # original tags should not contain 'new'
        original = next(u for u in fresh if u['name'] == 'Alice')
>       assert 'new' not in original['tags']
E       AssertionError: assert 'new' not in ['a', 'new']

tests/test_autose_cache.py:34: AssertionError
=========================== short test summary info ============================
FAILED tests/test_autose_cache.py::test_ac2_modified_nested_not_cached - Asse...
1 failed, 229 passed in 0.76s

```

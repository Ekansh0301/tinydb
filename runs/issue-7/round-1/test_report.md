# Test report

Result: **FAIL**

New tests: test_ac1_limit_returns_at_most_n_documents, test_ac2_limit_preserves_storage_order, test_ac3_limit_omitted_returns_all_documents, test_ac4_limit_works_on_named_tables

- Failing on the base commit (expected for new behaviour): tests/test_autose_limit.py::test_ac1_limit_returns_at_most_n_documents, tests/test_autose_limit.py::test_ac2_limit_preserves_storage_order, tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables
- Tests passing on the new code: 231
- Failing on the new code: tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables

Gate findings:
- test suite does not pass: tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables

Last lines of the full suite run:
```
c4_limit_works_on_named_tables():
        """AC-4: Given a named table `logs` containing 8 matching documents, when `db.search(where('type') == 'log', limit=4, table='logs')` is executed, then the returned collection shall contain exactly 4 documents in storage order."""
        db = TinyDB(storage=MemoryStorage)
        logs_table = db.table('logs')
        logs_table.insert_multiple([{'type': 'log', 'id': i} for i in range(8)])
    
>       results = db.search(where('type') == 'log', limit=4, table='logs')
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: Table.search() got an unexpected keyword argument 'table'

tests/test_autose_limit.py:54: TypeError
=========================== short test summary info ============================
FAILED tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables - Typ...
1 failed, 231 passed in 0.50s

```


## Stopped
Stage 4 could not pass its check: test suite does not pass: tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables; these tests raise errors in the test code itself, not assertion failures: tests/test_autose_limit.py:54 TypeError; failing: tests/test_autose_limit.py::test_ac4_limit_works_on_named_tables

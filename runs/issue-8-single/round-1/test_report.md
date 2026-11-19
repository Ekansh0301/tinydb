# Test report

Result: **FAIL**

New tests: test_ac1_remove_by_ids_only, test_ac2_remove_by_cond_only, test_ac3_remove_by_cond_and_ids

- Failing on the base commit (expected for new behaviour): tests/test_autose_remove.py::test_ac3_remove_by_cond_and_ids
- Tests passing on the new code: 0
- Failing on the new code: none

Gate findings:
- test suite does not pass: E     File "/home/runner/work/tinydb/tinydb/tinydb/table.py", line 642 | E       +            # When both ``doc_ids`` and ``cond`` are provided we should only | E   IndentationError: expected an indented block after 'if' statement on line 641

Last lines of the full suite run:
```
exit code 4
ImportError while loading conftest '/home/runner/work/tinydb/tinydb/tests/conftest.py'.
tests/conftest.py:7: in <module>
    from tinydb.middlewares import CachingMiddleware
tinydb/__init__.py:30: in <module>
    from .database import TinyDB
tinydb/database.py:9: in <module>
    from .table import Table, Document
E     File "/home/runner/work/tinydb/tinydb/tinydb/table.py", line 642
E       +            # When both ``doc_ids`` and ``cond`` are provided we should only
E   IndentationError: expected an indented block after 'if' statement on line 641

```

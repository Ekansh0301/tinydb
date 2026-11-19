# Test report

Result: **FAIL**

New tests: test_ac1_modified_not_cached, test_ac2_modified_nested_not_cached

- Failing on the base commit (expected for new behaviour): tests/test_autose_cache.py::test_ac1_modified_not_cached, tests/test_autose_cache.py::test_ac2_modified_nested_not_cached
- Tests passing on the new code: 0
- Failing on the new code: none

Gate findings:
- test suite does not pass: E     File "/home/runner/work/tinydb/tinydb/tinydb/table.py", line 275 | E       docs = [ | E   IndentationError: unexpected indent

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
E     File "/home/runner/work/tinydb/tinydb/tinydb/table.py", line 275
E       docs = [
E   IndentationError: unexpected indent

```

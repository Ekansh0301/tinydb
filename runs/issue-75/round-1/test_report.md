# Test report

Result: **FAIL**

New tests: test_ac1_only_jackson_matches, test_ac2_case_sensitive, test_ac3_non_string_no_match, test_ac4_match_sonic, test_ac5_composable_and

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_only_jackson_matches, tests/test_autose_contains_text.py::test_ac2_case_sensitive, tests/test_autose_contains_text.py::test_ac3_non_string_no_match, tests/test_autose_contains_text.py::test_ac4_match_sonic, tests/test_autose_contains_text.py::test_ac5_composable_and
- Tests passing on the new code: 232
- Failing on the new code: tests/test_autose_contains_text.py::test_ac5_composable_and

Gate findings:
- test suite does not pass: tests/test_autose_contains_text.py::test_ac5_composable_and

Last lines of the full suite run:
```
...............                                                        [100%]
=================================== FAILURES ===================================
___________________________ test_ac5_composable_and ____________________________

    def test_ac5_composable_and():
        db = TinyDB(storage=MemoryStorage)
        db.insert_multiple([{'name': 'Jackson', 'active': True}, {'name': 'Jackson', 'active': False}])
>       res = db.search(where('name').contains_text('son').and_(where('active').equals(True)))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       AttributeError: 'QueryInstance' object has no attribute 'and_'

tests/test_autose_contains_text.py:42: AttributeError
=========================== short test summary info ============================
FAILED tests/test_autose_contains_text.py::test_ac5_composable_and - Attribut...
1 failed, 232 passed in 0.47s

```

# Test report

Result: **FAIL**

New tests: test_ac1_contains_text_basic, test_ac2_contains_text_case_sensitive, test_ac3_contains_text_non_string, test_ac4_contains_text_substring_start, test_ac5_contains_text_composable

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_contains_text_basic, tests/test_autose_contains_text.py::test_ac2_contains_text_case_sensitive, tests/test_autose_contains_text.py::test_ac3_contains_text_non_string, tests/test_autose_contains_text.py::test_ac4_contains_text_substring_start, tests/test_autose_contains_text.py::test_ac5_contains_text_composable
- Tests passing on the new code: 232
- Failing on the new code: tests/test_autose_contains_text.py::test_ac5_contains_text_composable

Gate findings:
- test suite does not pass: tests/test_autose_contains_text.py::test_ac5_contains_text_composable

Last lines of the full suite run:
```
active': True}, {'name': 'Jackson', 'active': False}])
>       result = db.search((where('name').contains_text('son')) & where('active').equals(True))
                                                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_autose_contains_text.py:42: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tinydb/queries.py:97: in __call__
    return self._test(value)
           ^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

_ = True

    def notest(_):
>       raise RuntimeError('Empty query was evaluated')
E       RuntimeError: Empty query was evaluated

tinydb/queries.py:180: RuntimeError
=========================== short test summary info ============================
FAILED tests/test_autose_contains_text.py::test_ac5_contains_text_composable
1 failed, 232 passed in 0.64s

```

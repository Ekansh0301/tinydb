# Test report

Result: **FAIL**

New tests: test_ac1_only_jackson_matches, test_ac2_case_sensitive, test_ac3_non_string_fields, test_ac4_substring_start, test_ac5_composability

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_only_jackson_matches, tests/test_autose_contains_text.py::test_ac2_case_sensitive, tests/test_autose_contains_text.py::test_ac3_non_string_fields, tests/test_autose_contains_text.py::test_ac4_substring_start, tests/test_autose_contains_text.py::test_ac5_composability
- Tests passing on the new code: 230
- Failing on the new code: tests/test_autose_contains_text.py::test_ac1_only_jackson_matches, tests/test_autose_contains_text.py::test_ac4_substring_start, tests/test_autose_contains_text.py::test_ac5_composability

Gate findings:
- test suite does not pass: tests/test_autose_contains_text.py::test_ac1_only_jackson_matches, tests/test_autose_contains_text.py::test_ac4_substring_start, tests/test_autose_contains_text.py::test_ac5_composability

Last lines of the full suite run:
```
                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_autose_contains_text.py:45: 
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
FAILED tests/test_autose_contains_text.py::test_ac1_only_jackson_matches - As...
FAILED tests/test_autose_contains_text.py::test_ac4_substring_start - Asserti...
FAILED tests/test_autose_contains_text.py::test_ac5_composability - RuntimeEr...
3 failed, 230 passed in 0.67s

```

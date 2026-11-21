# Test report

Result: **FAIL**

New tests: test_ac1_between_inclusive_match, test_ac2_between_bounds_inclusive, test_ac3_missing_or_none_field, test_ac4_numbers_between, test_ac5_strings_between, test_ac6_combination_with_and_not

- Failing on the base commit (expected for new behaviour): tests/test_autose_between.py::test_ac1_between_inclusive_match, tests/test_autose_between.py::test_ac2_between_bounds_inclusive, tests/test_autose_between.py::test_ac3_missing_or_none_field, tests/test_autose_between.py::test_ac4_numbers_between, tests/test_autose_between.py::test_ac5_strings_between, tests/test_autose_between.py::test_ac6_combination_with_and_not
- Tests passing on the new code: 233
- Failing on the new code: tests/test_autose_between.py::test_ac3_missing_or_none_field

Gate findings:
- test suite does not pass: tests/test_autose_between.py::test_ac3_missing_or_none_field

Last lines of the full suite run:
```
 _ _ _ _ _ _ 
tinydb/table.py:275: in search
    if cond(doc)
       ^^^^^^^^^
tinydb/queries.py:97: in __call__
    return self._test(value)
           ^^^^^^^^^^^^^^^^^
tinydb/queries.py:250: in <lambda>
    lambda value: runner(value),
                  ^^^^^^^^^^^^^
tinydb/queries.py:247: in runner
    return test(value)
           ^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

value = None

>       lambda value: low <= value <= high,
                      ^^^^^^^^^^^^^^^^^^^^
        ('between', self._path, freeze(low), freeze(high))
    )
E   TypeError: '<=' not supported between instances of 'int' and 'NoneType'

tinydb/queries.py:335: TypeError
=========================== short test summary info ============================
FAILED tests/test_autose_between.py::test_ac3_missing_or_none_field - TypeErr...
1 failed, 233 passed in 0.78s

```

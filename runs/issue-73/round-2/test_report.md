# Test report

Result: **PASS**

New tests: test_ac1_contains_text_matches, test_ac2_contains_text_case_sensitive, test_ac3_missing_field_no_match, test_ac4_none_value_no_match, test_ac5_non_string_no_match

- Failing on the base commit (expected for new behaviour): tests/test_autose_contains_text.py::test_ac1_contains_text_matches, tests/test_autose_contains_text.py::test_ac2_contains_text_case_sensitive, tests/test_autose_contains_text.py::test_ac3_missing_field_no_match, tests/test_autose_contains_text.py::test_ac4_none_value_no_match, tests/test_autose_contains_text.py::test_ac5_non_string_no_match
- Tests passing on the new code: 233
- Failing on the new code: none

Last lines of the full suite run:
```
exit code 0
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 92%]
.................                                                        [100%]
233 passed in 0.67s

```

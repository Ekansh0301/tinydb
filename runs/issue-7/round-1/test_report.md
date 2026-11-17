# Test report

Result: **FAIL**

New tests: test_ac1_limit_returns_at_most_limit_documents, test_ac2_limit_preserves_storage_order

- Failing on the base commit (expected for new behaviour): none
- Tests passing on the new code: 0
- Failing on the new code: none

Gate findings:
- no test for: AC-3, AC-4
- test suite does not pass: see output

Last lines of the full suite run:
```
c_module
    source_hash, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:339: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/ast.py:52: in parse
    return compile(source, filename, mode, flags,
E     File "/home/runner/work/tinydb/tinydb/tests/test_autose_search_limit.py", line 22
E       for i in range(1, 7):
E                            ^
E   IndentationError: expected an indented block after 'for' statement on line 22
=========================== short test summary info ============================
ERROR tests/test_autose_search_limit.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.38s

```

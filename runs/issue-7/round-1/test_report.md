# Test report

Result: **FAIL**

New tests: test_ac1_limit_returns_list, test_ac2_limit_returns_first_n_in_order

- Failing on the base commit (expected for new behaviour): none
- Tests passing on the new code: 0
- Failing on the new code: none

Gate findings:
- no test for: AC-3, AC-4, AC-5, AC-6 (found only: test_ac1_limit_returns_list, test_ac2_limit_returns_first_n_in_order). Every test must be named test_ac<N>_<what>, with N the criterion number
- test suite does not pass: E     File "/home/runner/work/tinydb/tinydb/tests/test_autose_search_limit.py", line 21 | E       assert [d['i'] for d in result] == list(range(10 | E                                                    ^ | E   SyntaxError: '(' was never closed | ERROR tests/test_autose_search_limit.py

Last lines of the full suite run:
```
e
    source_hash, co = _rewrite_test(fn, self.config)
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/site-packages/_pytest/assertion/rewrite.py:339: in _rewrite_test
    tree = ast.parse(source, filename=strfn)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/hostedtoolcache/Python/3.12.16/x64/lib/python3.12/ast.py:52: in parse
    return compile(source, filename, mode, flags,
E     File "/home/runner/work/tinydb/tinydb/tests/test_autose_search_limit.py", line 21
E       assert [d['i'] for d in result] == list(range(10
E                                                    ^
E   SyntaxError: '(' was never closed
=========================== short test summary info ============================
ERROR tests/test_autose_search_limit.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.48s

```

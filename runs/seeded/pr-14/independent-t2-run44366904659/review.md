# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The approach of adding an optional `limit` argument to `search()` is correct, but the implementation has two defects. First, when `limit` is set, the truncated list is stored in the query cache, so a later call to `search(cond)` without `limit` returns only the truncated results — violating "without limit nothing should change." Second, the truncation is inside `if is_cacheable()`, so non-cacheable queries ignore `limit` entirely and return all matches. I confirmed both by running snippets: cached no-limit search returned [0,1] instead of [0,1,2,3], and a non-cacheable query with limit=2 returned all 4 docs.

## Checks
- [fail] limit then no-limit via cache returns wrong (truncated) results: snippet: `db.search(where('a')==1, limit=2)` then `db.search(where('a')==1)` returned [0,1] instead of [0,1,2,3]
- [fail] non-cacheable query ignores limit: snippet: non-cacheable query with limit=2 returned all 4 docs instead of first 2
- [pass] new limit tests pass: `python -m pytest tests/test_limit_seed.py -q` exit code 0

## Findings
- (high) tinydb/table.py:295 Truncating `docs` inside `if is_cacheable()` poisons the query cache (later no-limit searches return truncated results) and makes non-cacheable queries ignore `limit` entirely.
- (low) tinydb/table.py:259 Docstring `:param cond:` section does not document the new `limit` parameter.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

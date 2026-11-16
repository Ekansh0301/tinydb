# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The diff adds an optional `limit` argument to `Table.search()` but has two serious implementation defects. First, the query cache key is just `cond`, not `(cond, limit)`, so searching with `limit=2` then without `limit` returns truncated cached results. Second, the truncation only happens inside `if is_cacheable():`, so non-cacheable queries ignore `limit` entirely. Both were confirmed with snippets. The full existing test suite passes, but the new seed tests do not cover these edge cases.

## Checks
- [fail] Cache key ignores limit: search(cond, limit=2) then search(cond) returns truncated results: Snippet: first search limit=2 returned [0,1], second search no limit returned [0,1] instead of [0,1,2,3,4]
- [fail] Non-cacheable queries ignore limit: Snippet: custom query with is_cacheable() returning False, search(nc, limit=2) returned 5 docs instead of 2
- [pass] Existing test suite still passes: python -m pytest tests/ -x -q -> 100% passed
- [pass] New seed tests pass: python -m pytest tests/test_limit_seed.py -v -> 6 passed

## Findings
- (high) tinydb/table.py:297 Cache key `cond` does not include `limit`, so cached results from a limited search are returned for unlimited searches.
- (high) tinydb/table.py:295 The `docs = docs[:limit]` truncation is inside `if is_cacheable():`, so non-cacheable queries completely ignore `limit`.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

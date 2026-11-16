# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR adds an optional `limit` parameter to `Table.search()` as requested, but introduces a critical cache consistency bug. The query cache key is only `cond`, not `(cond, limit)`, and when `limit` is set the truncated results are cached. Subsequent calls with a different `limit` (or no limit) return the cached truncated/full results, ignoring the requested limit. I verified both directions empirically: searching with `limit=2` then without limit returns only 2 docs; searching without limit then with `limit=2` returns all 4 docs. Negative `limit` values also produce unexpected slicing behavior.

## Checks
- [fail] search with limit=2 then without limit returns wrong cached result: python -c snippet: after db.search(where('a')==1, limit=2) on 5 matching docs, db.search(where('a')==1) returns only 2 docs instead of 5
- [fail] search without limit then with limit=2 returns wrong cached result: python -c snippet: after db.search(where('a')==1) on 4 matching docs, db.search(where('a')==1, limit=2) returns 4 docs instead of 2
- [fail] negative limit produces unexpected slicing: python -c snippet: db.search(where('a')==1, limit=-1) on 4 docs returns 3 docs
- [pass] new limit tests pass: python -m pytest tests/test_limit_seed.py -v: 6 passed

## Findings
- (high) tinydb/table.py:265 Cache key is only `cond`; when `limit` is set, truncated results are cached and returned on subsequent calls regardless of the requested limit, causing incorrect results.
- (medium) tinydb/table.py:295 Negative `limit` values cause `docs[:limit]` to drop the last |limit| documents instead of being rejected or treated as no limit.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

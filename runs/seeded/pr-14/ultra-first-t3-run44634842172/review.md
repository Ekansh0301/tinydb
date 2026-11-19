# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The implementation has a critical bug: the `limit` parameter is applied before caching results, causing subsequent searches with different limits (or no limit) to return incorrectly truncated cached results. The cache should store full results, and the limit should be applied only when returning results to the caller.

## Checks
- [pass] All existing tests pass: python -m pytest tests/ -v --tb=short -> 234 passed
- [pass] New limit tests pass: python -m pytest tests/test_limit_seed.py -v -> 6 passed
- [fail] Cache bug: first search with limit=2 caches only 2 results: python -c 'from tinydb import TinyDB, where; db=TinyDB(":memory:"); db.insert_multiple([{"a":1,"i":i} for i in range(5)]); db.search(where("a")==1, limit=2); print([d["i"] for d in list(db._query_cache.values())[0]]) -> [0, 1]'
- [fail] Cache bug: subsequent search without limit returns cached truncated results: python -c 'from tinydb import TinyDB, where; db=TinyDB(":memory:"); db.insert_multiple([{"a":1,"i":i} for i in range(5)]); db.search(where("a")==1, limit=2); print([d["i"] for d in db.search(where("a")==1)]) -> [0, 1] (should be [0,1,2,3,4])'

## Findings
- (high) tinydb/table.py:295 The limit is applied before caching (line 295-296), causing the cache to store truncated results. Subsequent searches with different limits or no limit return incorrect cached data.
- (high) tinydb/table.py:265 The cache lookup (line 265-267) returns cached results without considering the current limit parameter, so a cached limited result is returned even when no limit is requested.
- (medium) tinydb/table.py:249 The docstring for the search method was not updated to document the new limit parameter.

_Reviewer model: nvidia:nvidia/nemotron-3-ultra-550b-a55b_

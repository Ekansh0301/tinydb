# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The `limit` parameter implementation has a critical cache bug: the cache key doesn't include the `limit` value, causing incorrect results when the same query is run with different limits. If a limited search runs first, subsequent unlimited searches return only the limited results. If an unlimited search runs first, subsequent limited searches return all results instead of the limit.

## Checks
- [pass] Tests pass: python -m pytest tests/ -v --tb=short -> 234 passed
- [fail] Cache bug with limit parameter: python -c 'from tinydb import TinyDB, where; db=TinyDB(":memory:"); db.insert_multiple([{"a":1,"i":i} for i in range(10)]); print(db.search(where("a")==1, limit=3)); print(db.search(where("a")==1))' -> second search returns 3 instead of 10
- [fail] Cache bug reverse order: python -c 'from tinydb import TinyDB, where; db=TinyDB(":memory:"); db.insert_multiple([{"a":1,"i":i} for i in range(10)]); print(db.search(where("a")==1)); print(db.search(where("a")==1, limit=3))' -> second search returns 10 instead of 3

## Findings
- (high) tinydb/table.py:265 Cache key doesn't include limit parameter. Line 265-267 returns cached results without checking if the limit matches. Line 295-297 caches truncated results when limit is set, polluting the cache for future unlimited searches.
- (medium) tests/test_limit_seed.py:1 Tests don't cover cache interaction with limit parameter. Need tests for: search with limit then without, search without limit then with, different limits on same query.

_Reviewer model: nvidia:nvidia/nemotron-3-ultra-550b-a55b_

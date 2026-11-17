# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The approach (optional `limit` on `search()`) is sound, but the implementation has three defects: (1) `limit` is only applied inside `if is_cacheable():`, so non-cacheable queries ignore it; (2) `docs` is truncated before being cached, poisoning the cache so a later call without `limit` returns truncated results; (3) the cache-hit path returns cached results without applying `limit`. I proved all three with snippets: `cached with limit=2` returned all 5 docs, and `second no limit` returned only 2 docs after a prior limited search.

## Checks
- [fail] limit applied on cache hit: snippet: `db.search(where('a')==1)` caches all 5, then `db.search(where('a')==1, limit=2)` returned [0,1,2,3,4] instead of [0,1]
- [fail] cache not poisoned by limit: snippet: after `db.search(where('a')==1, limit=2)`, a subsequent `db.search(where('a')==1)` returned [0,1] instead of all 5
- [pass] existing test suite passes: `python -m pytest tests/` exit code 0, 84 tests passed
- [pass] new limit tests pass: `python -m pytest tests/test_limit_seed.py` exit code 0, 6 tests passed

## Findings
- (high) tinydb/table.py:295 `limit` truncation is inside `if is_cacheable():`, so non-cacheable queries ignore `limit`; truncating `docs` before caching poisons the cache for later unlimited searches; the cache-hit path at line 267 returns cached results without applying `limit`.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

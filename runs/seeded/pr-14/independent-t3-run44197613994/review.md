# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR adds an optional `limit` argument to `Table.search()` as requested, but applies `limit` before populating the query cache and never re-applies it on cache hits. This breaks consistency: an unlimited search followed by a limited one ignores the limit, and a limited search followed by an unlimited one wrongly returns only the truncated cached results. The fix is to cache the full result set and apply `limit` at return time.

## Checks
- [fail] limit is ignored on a cache hit after an unlimited search: snippet: `limited after unlimited: [0, 1, 2, 3, 4]`
- [fail] an unlimited search after a limited one is wrongly truncated by the cache: snippet: `unlimited after limited (cached): 2 [0, 1]`
- [pass] new limit tests pass: `python -m pytest tests/test_limit_seed.py` → 6 passed
- [pass] full existing suite still passes: `python -m pytest tests/` → all pass

## Findings
- (high) tinydb/table.py:295 limit is applied before caching and not re-applied on cache hits, causing inconsistent results across repeated searches with different limits.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

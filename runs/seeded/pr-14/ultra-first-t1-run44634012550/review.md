# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The `limit` parameter is added to `search()` but interacts incorrectly with the query cache: results are truncated before being cached, and `limit` is ignored on cache hits. This makes behavior depend on call order — searching with a limit first then without returns too few results, and searching without a limit first then with a limit returns too many. The cache must store full results and `limit` must be applied at return time for both cache hits and misses.

## Checks
- [fail] search with limit then without limit returns wrong count: snippet: db.search(where('a')==1, limit=2) then db.search(where('a')==1) returned len=2 instead of 5
- [fail] search without limit then with limit returns wrong count: snippet: db.search(where('a')==1) then db.search(where('a')==1, limit=2) returned len=5 instead of 2
- [fail] named table limit then no limit returns wrong count: snippet: t.search(where('a')==1, limit=2) then t.search(where('a')==1) returned len=2 instead of 3
- [pass] test suite passes: python -m pytest tests/ -q exit code 0

## Findings
- (high) tinydb/table.py:295 Results are truncated (docs[:limit]) before being stored in the query cache, and limit is ignored on cache hits, causing inconsistent results depending on call order.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

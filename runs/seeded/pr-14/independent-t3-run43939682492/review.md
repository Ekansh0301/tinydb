# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The `limit` parameter is added correctly, but truncation happens before caching, so a limited search poisons the query cache and subsequent unlimited searches return wrong (truncated) results. This violates the "without limit nothing should change" requirement. The fix is to cache full results and truncate only the returned copy.

## Checks
- [fail] Cache poisoning: limited search corrupts later unlimited search: Snippet: after db.search(where('a')==1, limit=2) on 5 matching docs, db.search(where('a')==1) returns 2 docs instead of 5
- [pass] New limit tests pass: python -m pytest tests/test_limit_seed.py -v -> 6 passed
- [pass] Existing test suite still passes: python -m pytest tests/ -q -> 100% passed

## Findings
- (high) tinydb/table.py:295 Truncating docs before caching means a limited search caches truncated results, and later unlimited searches for the same cond return the truncated cache instead of all matches.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The `limit` parameter is added correctly to `Table.search`, but the query cache returns early before the limit check, so cached queries ignore `limit` entirely (invalid limits aren't validated, valid limits are silently dropped). This breaks the feature for any repeated search, which is exactly what the cache is for.

## Checks
- [pass] New limit tests pass: python -m pytest tests/test_autose_limit.py -v -> 4 passed
- [pass] Full test suite passes (no regressions): python -m pytest tests/ -q -> all passed
- [fail] Cached query ignores limit (defect): snippet: after caching a query, db.search(cond, limit=2) returned 5 docs instead of 2; limit=-1 did not raise

## Findings
- (high) tinydb/table.py:267 The query cache returns cached_results[:] before limit validation/application, so cached searches ignore limit entirely.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

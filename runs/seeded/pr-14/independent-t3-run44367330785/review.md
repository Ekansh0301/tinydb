# Review

Verdict: **REQUEST_CHANGES**
Problem class: code

The PR adds an optional `limit` argument to `Table.search()` and the new tests pass, but the implementation truncates `docs` inside the cache block before storing into `self._query_cache`. This poisons the query cache: a limited search followed by an unlimited search returns the truncated results (verified: `limit=2` then unlimited returns 2 instead of 4). The fix is to cache the full `docs` and apply `limit` only to the returned list for both cached and fresh paths.

## Checks
- [pass] New limit tests pass: python -m pytest tests/test_limit_seed.py -q → 6 passed
- [fail] Cache poisoning: limited then unlimited search returns wrong count: snippet: db.search(where('a')==1, limit=2) then db.search(where('a')==1) → 2, expected 4
- [pass] Full test suite passes: python -m pytest -q → all tests pass

## Findings
- (high) tinydb/table.py:295 Truncating `docs` inside `if is_cacheable():` before `self._query_cache[cond] = docs[:]` poisons the cache, so subsequent unlimited searches return truncated results.

_Reviewer model: nvidia:nvidia/nemotron-3.5-super-vl-120b-a12b_

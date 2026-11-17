# Design
## Approach
We will extend the `Table.search` method to accept an optional `limit` keyword argument while preserving its existing signature for callers that omit it. The method will first retrieve (or compute) the full list of matching documents, then apply the `limit` rules: a non‑positive limit yields an empty list, a positive limit returns at most that many documents in the original storage order, and a limit larger than the result size returns the full list. The cache will continue to store the full result set so that subsequent calls without a limit can reuse it, and calls with a limit will return a sliced copy. No other components need to change, and the public API of `TinyDB` already forwards unknown attributes to the default `Table`, so the new keyword works for named tables as well.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Change signature to `def search(self, cond: QueryLike, limit: int | None = None) -> list[Document]`.<br>• Add handling after the full result list is built: if `limit` is not `None` and `limit <= 0` return `[]`; if `limit` is positive return `result[:limit]`.<br>• Keep caching of the full result (as before) and slice only on return, so cached data remains unchanged.<br>• Update docstring to describe the new `limit` parameter and its behaviour. | AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 |
| tinydb/__init__.py | (re‑export) | No change needed; the new signature is automatically exposed via `TinyDB.search`. | – |

## Existing tests affected
None. All current tests exercise `Table.search` without the `limit` argument, and the default behaviour (no limit) is preserved. New tests for the limit feature will be added separately.

## Risks
- Slicing the cached result could unintentionally expose a view that mutates the cache; we return a fresh list slice to avoid this.  
- Adding a new keyword may conflict with user code that previously passed a positional argument named `limit`; however, `limit` is a keyword‑only addition, and existing positional calls remain unaffected.  
- The order of documents is defined by the iteration order of `self._read_table().items()`, which reflects the storage order; if a storage implementation changes this order, the limit behaviour will follow it, satisfying the spec.

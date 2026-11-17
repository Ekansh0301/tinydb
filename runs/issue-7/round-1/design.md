# Design
## Approach
Add an optional `limit` keyword argument to `Table.search`, which is the method ultimately invoked by `TinyDB.search`. The function will keep its existing caching behaviour – the cache stores the full result list for a given query – and will apply the `limit` only when returning the final list to the caller. Validation will ensure that a provided limit is a non‑negative integer, raising `ValueError` for negative values and `TypeError` for non‑integers. Because `TinyDB.__getattr__` forwards unknown attributes to the default table, no changes are required there, and the new signature works transparently for named tables as well.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Add `limit: int | None = None` keyword argument.<br>• Validate `limit` (raise `TypeError` if not `int`, `ValueError` if < 0).<br>• After obtaining the cached/full result list, slice it: `result = result[:limit]` when `limit` is not `None`.<br>• Update docstring to describe the new argument and behaviour. | AC-1, AC-2, AC-3, AC-4 |

## Existing tests affected
none – all current tests exercise `search` without a `limit` argument, and the added default behaviour preserves the existing output.

## Risks
- Introducing the `limit` parameter changes the public signature; callers that previously passed an unexpected keyword named `limit` will now be accepted, but this is intended and does not break existing code.
- Slicing after cache retrieval means the cached list remains the full result set, preserving cache correctness for subsequent calls with different limits. No cache invalidation logic is altered.

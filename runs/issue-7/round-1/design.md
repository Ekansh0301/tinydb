# Design
## Approach
Add an optional `limit` keyword to `Table.search`, validating that it is a non‑negative integer. The method will continue to use the existing query‑cache for the full result set, then apply the limit when returning a copy to the caller. This preserves current behaviour when `limit` is omitted and works for both the default and named tables because all table objects share the same `search` implementation. No other modules need changes.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | • Change signature to `def search(self, cond: QueryLike, limit: int | None = None) -> list[Document]`.<br>• Add validation: if `limit` is not `None` and not an `int` or is negative, raise `ValueError('limit must be a non‑negative integer')`.<br>• After obtaining `docs` (the full matching list) and before caching, store the full list in the cache as before.<br>• Return `docs[:limit]` when `limit` is provided, otherwise return a full copy (`docs[:]`). This keeps the cache unchanged and satisfies ordering. | AC‑1, AC‑2, AC‑3, AC‑4 |
| tinydb/__init__.py | (none) | No changes required; the public API forwards to `Table.search`, which now accepts `limit`. | – |
| tinydb/tests (if any) | (none) | No test files need modification; existing tests will continue to pass, and new tests for the limit behaviour can be added without altering current ones. | – |

## Existing tests affected
none

## Risks
- Introducing a `ValueError` for invalid limits may surface in user code that previously passed non‑integer values; however, this aligns with the assumption A‑1 that limits must be non‑negative integers.
- Slicing after caching ensures the cache stores the full result set; if a future change relies on the cached list being exactly what was returned, it could be impacted, but current TinyDB usage only reads from the cache internally.

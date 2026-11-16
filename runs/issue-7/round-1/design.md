# Design
## Approach
We will extend the `Table.search` method to accept an optional keyword argument `limit`. The method will keep its existing signature for backward compatibility (positional `cond` only) and add `limit=None` as a keyword‑only parameter. The search logic will remain unchanged; after gathering all matching documents we will apply the `limit` semantics: a non‑positive limit yields an empty list, a limit larger than the result size returns the full list, otherwise the list is sliced to the requested size. The full result set will still be cached so that subsequent calls without a limit (or with a larger limit) benefit from the cache. No other modules need changes, and the default behaviour of `search()` stays identical.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | Change signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`. After building `docs`, add logic: if `limit` is not None, treat `limit <= 0` as empty list, else return `docs[:limit]`. Cache the full `docs` list unchanged. Update docstring to mention the new argument. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5, AC‑6, AC‑7 |

## Existing tests affected
none – existing tests call `search` without the new keyword, which continues to work unchanged.

## Risks
- Adding a keyword‑only parameter could break code that calls `search` with a positional second argument; however, the library never used a second positional argument, so this risk is minimal.
- Slicing after caching ensures cache size is unchanged, but if a future change relies on the cached list being exactly the returned list, tests may need adjustment (unlikely given current design).

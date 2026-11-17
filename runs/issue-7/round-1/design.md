# Design
## Approach
Add an optional `limit` keyword argument to `Table.search`. The method will validate the argument, raise `TypeError` for non‑int values, and return an empty list for zero or negative limits. The existing query‑result cache will continue to store the full result set; the `limit` will be applied only to the list returned to the caller, preserving current behaviour when omitted. No other components need changes because `TinyDB.__getattr__` forwards calls to the default `Table`, which now supports the new signature, and named tables use the same `Table.search`.

## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/table.py | Table.search | • Change signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`.<br>• Validate `limit`: if not `None` and not `int` → raise `TypeError`.<br>• If `limit` ≤ 0 → return `[]`.<br>• After obtaining (or retrieving from cache) the full result list, apply slicing `results[:limit]` when `limit` is a positive int.<br>• Update docstring to describe the new argument and its semantics. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5, AC‑6 |
| tinydb/__init__.py | (re‑export) | No change needed; `Table.search` is the public API. | – |

## Existing tests affected
None. All current tests exercise `Table.search` without the `limit` argument, and the added default preserves existing behaviour. New tests for the limit functionality will be added, but no existing test needs modification.

## Risks
- **Cache semantics:** The cache still stores the complete result set; applying `limit` after retrieval ensures cached data remains correct for subsequent unlimited searches.  
- **Signature compatibility:** Adding a keyword‑only `limit` argument is backward compatible because calls that previously passed only the condition remain valid.  
- **Performance:** Slicing a list is O(k); negligible for typical TinyDB usage.

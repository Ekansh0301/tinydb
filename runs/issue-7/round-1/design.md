# Design
## Approach
Add an optional `limit` keyword argument to `Table.search`, defaulting to `None`. The method will keep its existing behavior (query‑cache lookup, result generation) and, after obtaining the full list of matching documents, apply the limit logic: if `limit` is provided and ≤ 0 return an empty list; otherwise slice the list to at most `limit` items, preserving the original storage order. Because `TinyDB.__getattr__` forwards attribute access to the default table, the new signature automatically applies to `db.search`. No other components need changes, and the existing query‑cache remains valid because the cached value is the full result list; limiting is performed after cache retrieval.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | Extend signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`. After obtaining `result` (from cache or fresh computation), add logic: <br>```python\nif limit is None:\n    return result\nif limit <= 0:\n    return []\nreturn result[:limit]\n```<br>Keep existing docstring and cache behavior unchanged. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5, AC‑6 |
| tinydb/database.py | `__getattr__` forwarding (no code change) | No modification needed; forwarding already works for any keyword arguments passed to the default table’s `search`. | — |

## Existing tests affected
None. All current tests exercise `db.search` without a `limit` argument, and the default `limit=None` preserves existing behaviour, so no test modifications are required.

## Risks
- **Cache size impact** – limiting is applied after cache retrieval, so the cache still stores the full result list; this matches current design and does not violate any constraint.
- **Signature compatibility** – adding a keyword‑only `limit` preserves positional call compatibility; existing code that passed positional arguments will continue to work.
- **Future API misuse** – callers might pass `limit` as a positional argument; the keyword‑only design prevents accidental mis‑ordering while remaining backward‑compatible.

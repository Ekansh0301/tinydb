# Design
## Approach
We will extend the `Table.search` method to accept an optional keyword‑only argument `limit`. The method will continue to use the existing query‑cache unchanged, caching the full result set for each query. After obtaining (or retrieving) the full list of matching documents, we will apply the `limit` semantics: a non‑positive limit returns an empty list, a positive limit returns at most that many documents preserving the original order, and omitting the argument returns the complete list. Because `TinyDB.__getattr__` forwards calls to the default table, the new signature automatically applies to the database‑level `search` as well, satisfying named‑table support.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | • Change signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`.<br>• Update docstring to describe the new `limit` parameter and its behavior.<br>• After retrieving (or caching) the full result list, apply limit logic: if `limit` is `None` return full list copy; if `limit` ≤ 0 return `[]`; else return `full_list[:limit]`.<br>• Ensure the full result list is still stored in the query cache unchanged. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5, AC‑6, AC‑7 |
| tinydb/__init__.py | (re‑export) | No change needed – the new signature propagates automatically. | – |
| tinydb/tests (if any) | (none) | No existing test files need modification; default behaviour is unchanged. | – |

## Existing tests affected
none – the default behaviour (no `limit` argument) is preserved, and the cache continues to store the full result set.

## Risks
- Adding a keyword‑only parameter could break user code that called `search` with a second positional argument (unlikely given current API).  
- Slicing the cached list creates a new list each call, which is already the case for uncached results; memory impact is negligible.  
- Ensure the cache still stores the full list so subsequent calls with different `limit` values see the same base data.

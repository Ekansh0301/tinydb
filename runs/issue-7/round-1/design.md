# Design
## Approach
We will extend the `Table.search` method to accept an optional keyword‑only argument `limit`. The method will validate the argument, raise `TypeError` for non‑int values and `ValueError` for negative ints, then apply the limit to the result list after the query is evaluated and cached. The cache will continue to store the full result set so repeated searches without a limit remain fast, while a limited call will simply slice the cached copy. Because `TinyDB.__getattr__` forwards unknown attributes to the default table, the new signature automatically supports `db.search(...)` and named tables via `db.table('name').search(...)`. No other components need changes, preserving all architectural constraints.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Add a keyword‑only parameter `limit: int | None = None`.<br>• Validate type (`isinstance(limit, int)`) → raise `TypeError` with clear message.<br>• Validate non‑negative (`limit >= 0`) → raise `ValueError` with clear message.<br>• After building `docs` and caching the full list, apply `limit` by returning `docs[:limit]` when `limit` is not `None`.<br>• Update docstring to describe the new argument and its behaviour. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5 |

## Existing tests affected
None. Existing tests that call `search` without `limit` continue to receive the full list because the default `limit=None` leaves behaviour unchanged. New tests for the limit functionality will need to be added, but no current test must be modified.

## Risks
- Slicing after caching could expose more documents than intended if a caller mutates the returned list; however, the method already returns a fresh copy of cached results, and slicing a copy preserves this guarantee.
- Adding a keyword‑only argument may break user code that called `search` with positional arguments beyond the condition; however, the original signature only accepted a single positional argument, so this change is backward‑compatible.

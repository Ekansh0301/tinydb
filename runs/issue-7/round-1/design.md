# Design
## Approach
Add an optional `limit` keyword argument to `Table.search`. The method will keep its existing caching behaviour by always caching the full result set, then apply the limit only to the returned list. A simple validation ensures `limit` is a non‑negative integer, raising `ValueError` for invalid values. Because `TinyDB.__getattr__` forwards attribute access to the default `Table`, no changes are needed there, and the new argument automatically works for named tables via `TinyDB.table(name).search(...)`.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Extend signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`.<br>• Validate `limit` (must be `int` and ≥ 0) and raise `ValueError` otherwise.<br>• After obtaining (or caching) the full result list, return `docs[:limit]` when `limit` is not `None`; otherwise return the full list.<br>• Update docstring to describe the new argument and its behaviour. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5 |

## Existing tests affected
none – all current tests exercise the original behaviour (no `limit` argument) which remains unchanged. New tests for the `limit` feature will be added separately.

## Risks
- Introducing a new parameter could clash with existing user‑defined `search` wrappers that expect only one positional argument; however, the keyword‑only nature (`*, limit`) preserves backward compatibility.
- Incorrect handling of the cache could cause limited results to be cached; the implementation caches the full result set before slicing, avoiding this risk.

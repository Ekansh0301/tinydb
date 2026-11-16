# Design
## Approach
Add an optional keyword‑only `limit` argument to `Table.search`. The method will validate the argument (must be an `int` ≥ 0, otherwise raise `TypeError` or `ValueError`), then perform the existing search logic unchanged, cache the full result set, and finally apply the limit to the returned list. Because the default table is accessed via `TinyDB.__getattr__`, the new signature automatically works for named tables as well. No other components need modification, preserving all architectural constraints.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Change signature to `def search(self, cond: QueryLike, *, limit: int | None = None) -> list[Document]`.<br>• Add validation: raise `TypeError` if `limit` is not an `int`; raise `ValueError` if `limit` < 0.<br>• After computing `docs` and caching the full result, apply `limit` (`return docs[:limit]` if provided).<br>• Update docstring to describe the new parameter and its behaviour. | AC‑1, AC‑2, AC‑3, AC‑4, AC‑5 |
| tinydb/__init__.py | (none) | No change needed; forwarding to default table already picks up the new signature. | – |
| tinydb/tests (if any) | (none) | No existing test needs modification; new behaviour is additive. | – |

## Existing tests affected
none – the change is additive and preserves the original behaviour when `limit` is omitted, so all current tests should continue to pass.

## Risks
- Introducing a keyword‑only parameter could break user code that calls `search` with positional arguments beyond `cond`. However, TinyDB’s public API only ever passed a single positional argument, so impact is minimal.  
- The limit slicing occurs after caching; if a future change expects the cache to store limited results, this could diverge, but current architecture (cache stores full result) remains intact.


## Stopped
Stage 2 could not pass its check: acceptance criteria not covered by any row: AC-1, AC-2, AC-3, AC-4, AC-5

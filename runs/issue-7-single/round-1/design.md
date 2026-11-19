# Design
## Approach
Add a `limit` keyword to `Table.search`. The method will still query the cache for the full result set; after obtaining the (cached or freshly computed) list, it will slice it according to `limit` before returning to the caller. This keeps cache contents unchanged (full result list) and satisfies the requirement that existing behaviour without `limit` is unchanged.

## Changes
| File | Function or class | Change | ACs |
| --- | --- | --- | --- |
| tinydb/table.py | `Table.search` | - Extend signature to `def search(self, cond: QueryLike, limit: int | None = None) -> list[Document]`. <br> - Update docstring to describe `limit`. <br> - After retrieving `docs` (either from cache or fresh computation), apply `if limit is not None: docs = docs[:limit]`. <br> - Return the possibly sliced list. | AC-1, AC-2, AC-3 |

## Existing tests affected
None directly; existing tests rely on the original signature, which still works because `limit` has a default value.

## Risks
- R1: Introducing a new parameter could break user code that passed a positional argument expecting the old signature. Mitigation: the new parameter is keyword‑only with a default, and the signature order keeps `cond` first, so existing positional calls remain valid.
- R2: Slicing after cache retrieval could return a truncated list that is then cached incorrectly if the cache logic is altered. Mitigation: cache insertion remains unchanged (`self._query_cache[cond] = docs[:]`) before slicing, preserving full result caching.
- R3: Type hint `int | None` requires Python 3.10+. The project already targets 3.10+, so no compatibility issue.

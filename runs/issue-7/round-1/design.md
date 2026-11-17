# Design
## Approach
We will extend `Table.search` to accept an optional keyword‑only argument `limit: int | None = None`. The method will keep its existing behaviour (including cache usage) unchanged when `limit` is omitted or `None`. After obtaining the full result list (and optionally caching it), we will apply the limit by returning `docs[:limit]` when a positive integer is provided, raising `ValueError` for non‑positive integers. Because the limit is applied after caching, existing cached full‑result sets remain valid for subsequent calls without a limit, satisfying FR‑2 and preserving order.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Add keyword‑only parameter `limit: int | None = None` to the signature.<br>• Validate `limit` (raise `ValueError` if not `None` and `limit <= 0`).<br>• Keep existing cache lookup and caching of the full result list unchanged.<br>• After building `docs` (and caching if appropriate), apply `if limit is not None: return docs[:limit]` otherwise return `docs`.<br>• Update docstring to describe the new argument and its behaviour. | AC‑1, AC‑2, AC‑3, AC‑4 |

## Existing tests affected
None. All current tests exercise `Table.search` without a `limit` argument, and the added keyword‑only parameter does not affect those calls.

## Risks
- Introducing the keyword‑only parameter could break code that previously passed a positional argument expecting the old signature; however, the spec mandates that `limit` be keyword‑only, and such usage would have been invalid before (no second positional argument existed), so risk is minimal.  
- If a user relied on the cached list being returned directly (i.e., mutating the list), the new slicing could return a new list even when `limit` is `None`. The implementation returns the original cached list copy (`cached_results[:]`) when no limit is set, preserving existing semantics.  
- Ensuring that the limit is applied after caching is crucial; otherwise cached limited results could affect later unrestricted searches. The plan explicitly applies the limit only to the return value.

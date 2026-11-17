# Design
## Approach
Add an optional `limit` keyword argument to `Table.search` while preserving its existing behavior when omitted. The function will validate `limit` as a non‑negative integer, raise `ValueError` for negatives, and return a sliced copy of the full result list when a limit is provided. Caching will continue to store the complete result set so that subsequent unlimited searches are fast, and the change will automatically apply to the default table and any named tables because they all use the same `Table.search` implementation. No other modules need to be altered.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | • Add `limit: int | None = None` to the signature.<br>• Validate that `limit` is `None` or a non‑negative int (raise `ValueError` if negative).<br>• After building `docs`, compute `result = docs if limit is None else docs[:limit]`.<br>• Return `result` (still a fresh copy).<br>• Keep caching unchanged (cache full `docs`). | AC-1, AC-2, AC-3, AC-4, AC-5 |

## Existing tests affected
none – all current tests call `search()` without `limit`; the new optional argument is backward‑compatible.

## Risks
- Slicing after document conversion may add minimal overhead, but it does not affect correctness.  
- Introducing a new parameter could conflict with user‑defined query objects that also accept `**kwargs`; however, `Table.search` only forwards `cond`, so this risk is negligible.  
- Validation may raise `ValueError` for negative limits, which is an intentional design decision (per assumption A‑1).

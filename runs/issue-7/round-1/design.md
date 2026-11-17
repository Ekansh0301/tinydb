# Design
## Approach
We will extend the `Table.search` method to accept an optional keyword‑only argument `limit`. The method will keep its existing behaviour (including caching) and only slice the result list when a non‑`None` limit is provided. Validation will ensure `limit` is a non‑negative integer, raising `ValueError` for negatives. Because `TinyDB.__getattr__` forwards unknown attributes to the default table, no change is required there; the new signature will be automatically usable on named tables as well.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Add a keyword‑only parameter `limit: int | None = None` to the signature.<br>• Validate `limit` (raise `ValueError` if < 0, allow 0).<br>• After building the full `docs` list and caching it (unchanged), return `docs[:]` when `limit is None` else `docs[:limit]`.<br>• Update docstring to describe the new argument and its behaviour. | AC-1, AC-2, AC-3, AC-4, AC-5 |
| tinydb/__init__.py (optional) | Re‑export unchanged | No change needed; the public API already exposes `TinyDB.search` which forwards to `Table.search`. | – |

## Existing tests affected
None. The current test suite never passes a `limit` argument, so all existing behaviour remains identical. No test modifications are required.

## Risks
- **Cache consistency:** The cache continues to store the full result set; slicing occurs only on return, preserving existing cache semantics.
- **Performance:** For very large tables the full list is still built before slicing, which matches the specification (no early‑exit optimisation required).  
- **Argument validation:** Introducing a `ValueError` for negative limits adds a new exception path; callers must handle it, but this is documented and aligns with the assumed behaviour.

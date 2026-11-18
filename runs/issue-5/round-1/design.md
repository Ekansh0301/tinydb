# Design
## Approach
The current `Table.search` method returns document objects that are stored directly in the per‑table query cache, so repeated searches return the same mutable instances. To satisfy FR‑1 and FR‑2 we will make `search` always return deep‑copied documents, ensuring in‑memory edits never affect later queries or the persisted database. The cache will store these deep copies, and each call will return a fresh list of those copies. This change does not affect storage, update logic, or the public API beyond the behaviour of `search`. No other component needs modification.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` | • Import `copy` at top.<br>• After building `docs`, replace caching line with `self._query_cache[cond] = [copy.deepcopy(d) for d in docs]`.<br>• When returning cached results, return `[copy.deepcopy(d) for d in cached_results]` (or simply `cached_results[:]` because they are already deep copies).<br>• Update docstring to note that returned documents are deep copies and must be treated as read‑only. | AC-1, AC-2 |
| tinydb/table.py | module level (add import) | `import copy` | AC-1, AC-2 |

## Existing tests affected
None identified. Existing tests that relied on object identity of cached results will still pass because the returned list is a new list; the underlying objects are now deep copies, which is the intended behaviour. No test modifications are required.

## Risks
- Increased memory usage due to deep‑copying documents for every search and cache entry.
- Very large nested documents may incur a performance penalty during copying.

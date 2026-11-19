# Design
## Approach
Modify `Table.search` to return deep copies of documents retrieved from the query‑result cache. Also store deep copies in the cache when populating it, preventing later modifications from leaking back into cached data. Use the standard library `copy.deepcopy` which handles nested structures.

## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | `Table.search` (result handling) | Import `copy`; when returning cached results, return `[self.document_class(copy.deepcopy(d), d.doc_id) for d in cached_results]` instead of shallow copies. | AC-1, AC-2 |
| tinydb/table.py | `Table.search` (cache population) | Store deep copies in the cache: `self._query_cache[cond] = [copy.deepcopy(d) for d in docs]` instead of a shallow slice. | AC-1, AC-2 |
| tinydb/table.py | top imports | Add `import copy` alongside existing imports. | AC-1, AC-2 |

## Existing tests affected
None; new tests replace the failing cache test.

## Risks
- Slight increase in memory usage due to deep copies, but acceptable for correctness.
- Ensure `copy.deepcopy` works with `Document` objects (they are dict subclasses); deep copying preserves `doc_id` attribute which is re‑attached via `Document` constructor.

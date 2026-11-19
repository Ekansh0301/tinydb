# Design
## Approach
Modify `Table.search` so that when a cached result is found, it returns new `Document` instances created from the cached data rather than the cached instances themselves. This prevents user‑side mutations from contaminating the cache. The change is limited to the cache‑hit branch; cache‑miss behavior remains unchanged.
## Changes
| File | Function or class | Change | ACs |
|---|---|---|---|
| tinydb/table.py | Table.search | Replace returning of cached list with a list comprehension that builds fresh `self.document_class` objects from each cached document's data and `doc_id`. | AC-1, AC-2 |
## Existing tests affected
- None (new tests added replace the previous failing behavior).
## Risks
- Risk 1: If cached entries are not plain `Document` objects but raw dicts, accessing `d.doc_id` may fail. Mitigated by using `self.document_class` which expects a mapping and an id; we retrieve `doc_id` from the cached document (which is a `Document`). If not, fallback to extracting `_id` from the underlying dict.
- Risk 2: Slight performance overhead on each cache hit due to object recreation; acceptable for correctness.
- Risk 3: Ensure that the modification does not break the cache invalidation logic; we only read from the cache, not write to it.

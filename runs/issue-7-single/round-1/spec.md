# Spec
## Source statements
S1: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored? Without `limit` nothing should change. It should work on named tables too."

## Requirements
- FR-1 [STATED] The `Table.search` method shall accept an optional `limit` argument (int or None). (S1)
- FR-2 [STATED] When `limit` is provided, `search` shall return at most `limit` documents, preserving the order in which they are stored. (S1)
- FR-3 [STATED] When `limit` is omitted or None, `search` shall behave exactly as before, returning all matching documents. (S1)

## Acceptance criteria
- AC-1 (FR-1, FR-2, FR-3): Given a table with more than five matching documents, when calling `table.search(query, limit=5)`, then the returned list length is 5 and the first five documents are the same as the first five items of `table.search(query)` without limit.
- AC-2 (FR-3): Given a table with matching documents, when calling `table.search(query)` (no limit argument), then the returned list is identical to the list returned before the change (all matches, same order). 

## Assumptions and open questions
- A-1 [ASSUMED] The existing `Table.search` implementation returns documents in insertion order (the order of the underlying dict iteration). Impact if wrong: limit would still return a prefix of that order, satisfying the requirement of “order they are stored”. 
- A-2 [ASSUMED] Adding a `limit` parameter does not affect the query‑cache semantics: the cache should still store the full result list, and the limit is applied after retrieving from the cache. Impact if wrong: cached results could be truncated, breaking subsequent unlimited searches. 

## Non-goals
- Adding pagination or offset support.
- Changing the underlying storage order semantics.

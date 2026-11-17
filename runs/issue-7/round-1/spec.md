# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S3: "Without `limit` nothing should change."  
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer (≥ 1). (S2)  
- FR-2 [STATED] When `limit` is supplied, `search()` shall return a sequence containing **at most** `limit` documents that satisfy the query, ordered by the internal storage order of the table. (S2)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall exhibit the same behavior as the current implementation (i.e., return all matching documents). (S3)  
- FR-4 [STATED] The `limit` argument shall be supported for searches on the default table and on any named table passed to `search()`. (S4)  

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=5)`, when the function is invoked, then the call completes without raising a TypeError and the returned object is iterable.  
- AC-2 (FR-2): Given a table containing 20 documents matching `where('type') == 'log'`, when `db.search(where('type') == 'log', limit=7)` is executed, then the returned sequence length is 7 and the documents appear in the same order as they are stored in the table.  
- AC-3 (FR-2): Given a table containing 3 documents matching the query, when `db.search(where('type') == 'log', limit=10)` is executed, then the returned sequence length is 3 (i.e., not more than the limit).  
- AC-4 (FR-3): Given a table with 15 matching documents, when `db.search(where('type') == 'log')` is executed (no limit argument), then the returned sequence length is 15, identical to the current behavior without the new feature.  
- AC-5 (FR-4): Given a named table `db.table('archive')` containing 12 matching documents, when `db.table('archive').search(where('type') == 'log', limit=4)` is executed, then the returned sequence length is 4 and the order matches the storage order of the `archive` table.  

## Assumptions and open questions
- A-1 [ASSUMED] The internal storage order is deterministic and observable via the existing `search()` results; otherwise “order they are stored” cannot be verified. Impact if wrong: the AC‑2 and AC‑5 checks may be flaky if storage order changes between calls. Question: Does the current implementation guarantee a stable order for identical queries?  

## Non-goals
- Pagination or offset handling beyond the simple `limit` parameter.  
- Changing the default ordering of results; the feature only preserves existing order.  
- Performance optimizations for limiting results; the implementation may still scan the full table internally.

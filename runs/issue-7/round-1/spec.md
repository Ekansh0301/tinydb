# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S3: "Without `limit` nothing should change."  
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer. (S2)  
- FR-2 [STATED] When `limit` is provided, `search()` shall return **no more than** `limit` documents, ordered by their physical storage order. (S2)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S3)  
- FR-4 [STATED] The `limit` argument shall be applicable regardless of whether the search is performed on the default table or on a named table. (S4)  
- FR-5 [INFERRED] If `limit` is less than or equal to zero, `search()` shall return an empty list. (S2, S3)  
- FR-6 [INFERRED] If `limit` is greater than the total number of matching documents, `search()` shall return all matching documents. (S2)

## Acceptance criteria
- AC-1 (FR-1): Given a database instance `db`, when calling `db.search(where('type') == 'log', limit=5)`, then the call returns a list object and the function signature includes a `limit` parameter.  
- AC-2 (FR-2): Given a database containing 20 documents that satisfy `where('type') == 'log'`, when calling `db.search(where('type') == 'log', limit=10)`, then the returned list length is exactly 10 and the documents appear in the same order as they are stored in the underlying storage engine.  
- AC-3 (FR-3): Given the same database, when calling `db.search(where('type') == 'log')` (no `limit` argument), then the returned list length is 20, matching the current behavior without `limit`.  
- AC-4 (FR-4): Given a named table `logs` with 15 matching documents, when calling `db.search(where('type') == 'log', limit=7, table='logs')`, then the returned list length is 7 and the documents are from the `logs` table in storage order.  
- AC-5 (FR-5): Given any database, when calling `db.search(where('type') == 'log', limit=0)`, then the returned list is empty (`len(result) == 0`).  
- AC-6 (FR-6): Given a database with 8 matching documents, when calling `db.search(where('type') == 'log', limit=20)`, then the returned list length is 8 (all matches).  

## Assumptions and open questions
- A-1 [ASSUMED] “order they are stored” refers to the order defined by the underlying storage engine’s natural iteration order (e.g., insertion order for append‑only stores). Impact if wrong: Tests may fail because the observed order differs; clarification needed on whether a stable sort key is required. Question: Is there an existing API to retrieve the storage order, or must a deterministic order be defined for this feature?  
- A-2 [ASSUMED] The `search()` function currently returns a plain Python list; the new `limit` argument will not change the return type. Impact if wrong: If `search()` returns a generator or custom collection, the acceptance criteria need adjustment. Question: What is the exact return type of `search()` in the current implementation?  

## Non-goals
- Changing the default ordering of results when `limit` is not supplied.  
- Adding pagination metadata (e.g., total count, offset).  
- Supporting `limit` on non‑table queries such as raw SQL strings.  
- Performance optimizations beyond ensuring that the limit does not cause full result materialization.

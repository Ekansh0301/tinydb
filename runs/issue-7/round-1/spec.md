# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S3: "Without `limit` nothing should change."  
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit`. (S2)  
- FR-2 [STATED] When a positive integer `limit` is supplied, `search()` shall return **at most** `limit` documents that satisfy the query, preserving the order in which the documents are stored. (S2)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S3)  
- FR-4 [STATED] The `limit` argument shall be supported for searches on the default table as well as on any named table. (S4)  

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log')`, when the call is executed, then the function signature includes a keyword argument `limit` that can be passed without raising a `TypeError`.  
- AC-2 (FR-2): Given a call `db.search(where('type') == 'log', limit=5)`, when the query matches 12 documents, then the returned list length is `5` and the first 5 elements are the same as the first 5 elements of the list returned by `db.search(where('type') == 'log')`.  
- AC-3 (FR-2): Given a call `db.search(where('type') == 'log', limit=0)`, when the query matches any documents, then the returned list length is `0`.  
- AC-4 (FR-3): Given a call `db.search(where('type') == 'log')` before and after the implementation of `limit`, when the same database state is used, then the two returned lists are identical in content and order.  
- AC-5 (FR-4): Given a call `db.search(where('type') == 'log', limit=3, table='archive')`, when the named table `archive` contains 8 matching documents, then the returned list length is `3` and the elements correspond to the first three stored documents in `archive`.  

## Assumptions and open questions
- A-1 [ASSUMED] `limit` will be validated as a non‑negative integer; negative values will raise a `ValueError`. Impact if wrong: callers might receive unexpected results or uncaught exceptions. Question: Should negative limits be treated as zero, ignored, or cause an error?  
- A-2 [ASSUMED] The order “in which they are stored” is the same order currently used by `search()` when returning all results. Impact if wrong: The returned subset could appear out of expected order, breaking UI expectations. Question: Does the storage order ever differ from the order of iteration in the existing implementation?  

## Non-goals
- Pagination mechanisms beyond a simple `limit` (e.g., offset, cursor).  
- Changing the underlying storage order or providing sorting options.  
- Performance optimizations for large limits; the implementation may still scan all matching documents.

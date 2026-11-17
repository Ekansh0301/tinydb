# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S3: "Without `limit` nothing should change."  
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit`. (S2)  
- FR-2 [STATED] When a positive integer `limit` is supplied, `search()` shall return **at most** `limit` documents, preserving the order in which the documents are stored. (S2)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S3)  
- FR-4 [STATED] The `limit` argument shall be supported for searches on both the default table and any named table. (S4)  

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log')`, when the call includes `limit=5`, then the returned list length shall be ≤ 5.  
- AC-2 (FR-2): Given a dataset where documents are stored in order D1, D2, D3, D4, D5, D6, when `db.search(where('type') == 'log', limit=3)` is executed, then the returned list shall be `[D1, D2, D3]`.  
- AC-3 (FR-3): Given a call `db.search(where('type') == 'log')` without a `limit` argument, when the call is executed on a database containing 12 matching documents, then the returned list shall contain exactly 12 documents, identical to the current implementation.  
- AC-4 (FR-4): Given a named table `logs` with 8 matching documents, when `db.search(where('type') == 'log', limit=4, table='logs')` is executed, then the returned list shall contain exactly the first 4 documents of that table in storage order.  

## Assumptions and open questions
- A-1 [ASSUMED] `limit` must be a non‑negative integer. Impact if wrong: If callers pass non‑integer or negative values, the function may raise a TypeError or behave unpredictably. Question: Should the function raise a `ValueError` for negative limits or coerce them to zero?  
- A-2 [ASSUMED] The storage order is defined by the internal insertion order of documents. Impact if wrong: If the underlying storage uses a different ordering (e.g., primary‑key order), the returned subset may not match user expectations. Question: Is “order they are stored” synonymous with insertion order, and is that order stable across restarts?  
- A-3 [ASSUMED] The existing `search()` signature permits additional keyword arguments; adding `limit` will not break backward compatibility. Impact if wrong: Existing code that passes unexpected keyword arguments could raise errors. Question: Does the current implementation already reject unknown keywords?  

## Non-goals
- Implementing pagination or offset handling.  
- Changing the default ordering of search results.  
- Providing server‑side streaming of results beyond the `limit` functionality.

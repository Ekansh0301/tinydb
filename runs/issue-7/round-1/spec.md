# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S3: "Without `limit` nothing should change."  
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit`. (S2)  
- FR-2 [STATED] When a positive integer `limit` is supplied, `search()` shall return **at most** that many documents, preserving the order in which the documents are stored. (S2)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S3)  
- FR-4 [STATED] The `limit` argument shall be supported for searches on both the default table and any named table. (S4)  

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log')`, when the call includes `limit=5`, then the returned collection length shall be ≤ 5.  
- AC-2 (FR-2): Given a dataset where documents are stored in order D1, D2, D3, D4, D5, D6, when `db.search(where('type') == 'log', limit=3)` is executed, then the returned list shall be `[D1, D2, D3]`.  
- AC-3 (FR-3): Given a call `db.search(where('type') == 'log')` without a `limit` argument, when the call is executed on a database containing 12 matching documents, then the returned collection shall contain exactly 12 documents.  
- AC-4 (FR-4): Given a named table `logs` containing 8 matching documents, when `db.search(where('type') == 'log', limit=4, table='logs')` is executed, then the returned collection shall contain exactly 4 documents in storage order.  

## Assumptions and open questions
- A-1 [ASSUMED] `limit` must be a non‑negative integer. Impact if wrong: If callers pass non‑integer or negative values, the function may raise a TypeError or behave unpredictably. Question: Should the API raise a specific exception (e.g., `ValueError`) for invalid limits?  
- A-2 [ASSUMED] The storage order is the order defined by the underlying database iterator (e.g., insertion order). Impact if wrong: If the database does not guarantee a deterministic order, the “order they are stored” requirement may be ambiguous. Question: Is a stable ordering guaranteed for all back‑ends?  
- A-3 [ASSUMED] The `limit` argument does not affect other side effects of `search()` (e.g., cursor opening, logging). Impact if wrong: Additional side effects could change performance characteristics. Question: Should any performance metrics be part of the specification?  

## Non-goals
- Implementing pagination or offset handling beyond the simple `limit` parameter.  
- Changing the default ordering of results; the specification only preserves existing storage order.  
- Providing a `limit` argument for non‑search related APIs.

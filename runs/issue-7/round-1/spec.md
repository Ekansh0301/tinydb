# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."  
S2: "`first_ten = db.search(where('type') == 'log')[:10]`"  
S3: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S4: "Without `limit` nothing should change."  
S5: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer. (S3)  
- FR-2 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S4)  
- FR-3 [STATED] When `limit` is provided, `search()` shall return **at most** `limit` documents. (S3)  
- FR-4 [INFERRED] The documents returned when `limit` is used shall be ordered in the same order as they are stored in the underlying table. (S3)  
- FR-5 [INFERRED] The `limit` argument shall be applicable to searches on both the default table and any named table supplied to `search()`. (S5)  

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=5)`, when the function executes, then the returned list length shall be ≤ 5.  
- AC-2 (FR-2): Given a call `db.search(where('type') == 'log')` on a database containing 12 matching documents, when the function executes, then the returned list length shall be 12.  
- AC-3 (FR-3): Given a call `db.search(where('type') == 'log', limit=0)`, when the function executes, then the returned list shall be empty (`len(result) == 0`).  
- AC-4 (FR-4): Given a table where documents are stored in order `[docA, docB, docC, docD]` and a query that matches all four, when `db.search(query, limit=2)` is called, then the returned list shall be `[docA, docB]`.  
- AC-5 (FR-5): Given a named table `errors` containing 8 matching rows, when `db.search(where('type') == 'error', limit=3, table='errors')` is called, then the returned list length shall be 3 and the items shall be the first three rows in storage order of that table.  

## Assumptions and open questions
- A-1 [ASSUMED] The `limit` argument must be a non‑negative integer. Impact if wrong: If callers pass non‑integer or negative values, the function may raise a TypeError or behave unpredictably. Question: Should the API raise a specific exception for invalid `limit` values?  
- A-2 [ASSUMED] If `limit` exceeds the number of matching documents, the function shall return all matches without error. Impact if wrong: Could cause unexpected truncation if implementation treats `limit` as an absolute maximum regardless of match count. Question: Is there a requirement to signal that the limit was larger than the result set?  

## Non-goals
- Changing the underlying storage order or providing sorting capabilities beyond the existing storage order.  
- Adding pagination metadata (e.g., total count, offset) to the `search()` return value.  
- Supporting `limit` on aggregate or non‑document queries that currently do not return a list of documents.

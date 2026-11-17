# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."
S2: "`first_ten = db.search(where('type') == 'log')[:10]`"
S3: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S4: "Without `limit` nothing should change."
S5: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer. (S3)  
- FR-2 [STATED] When `limit` is provided, `search()` shall return at most `limit` documents, preserving the order in which the documents are stored. (S3)  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents. (S4)  
- FR-4 [STATED] The `limit` argument shall be applicable when `search()` is invoked on any table, including named tables. (S5)  
- FR-5 [INFERRED] If `limit` is a non‑positive integer (zero or negative), `search()` shall return an empty list. (S3)  
- FR-6 [INFERRED] If `limit` is not an integer, `search()` shall raise a `TypeError`. (S3)

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=10)`, when the function is executed, then the call completes without raising an exception and the returned object is a list.  
- AC-2 (FR-2): Given a table containing 25 matching documents, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list contains exactly 10 documents ordered identically to their storage order.  
- AC-3 (FR-3): Given a call `db.search(where('type') == 'log')` (no `limit` argument), when the function is executed, then the returned list contains all matching documents (e.g., 25 in the above scenario).  
- AC-4 (FR-4): Given a named table `logs` with 15 matching documents, when `db.search(where('type') == 'log', limit=5, table='logs')` is called, then the returned list contains exactly 5 documents from that named table in storage order.  
- AC-5 (FR-5): Given a call `db.search(where('type') == 'log', limit=0)`, when the function is executed, then the returned list is empty (`len(result) == 0`).  
- AC-6 (FR-6): Given a call `db.search(where('type') == 'log', limit='ten')`, when the function is executed, then a `TypeError` is raised.

## Assumptions and open questions
- A-1 [ASSUMED] The phrase “in the order they are stored” refers to the natural iteration order of the underlying storage engine (e.g., insertion order). Impact if wrong: If the system defines a different default ordering (e.g., primary‑key order), the implementation may need to sort accordingly, affecting performance. Question: What exact ordering semantics does the current `search()` use when no explicit ordering is specified?  

## Non-goals
- Changing the default ordering of `search()` results.  
- Adding pagination or offset support beyond the simple `limit` parameter.  
- Modifying the API of `where()` or other query‑building helpers.

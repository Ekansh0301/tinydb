# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."
S2: "`first_ten = db.search(where('type') == 'log')[:10]`"
S3: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S4: "Without `limit` nothing should change."
S5: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer. (S3)  
- FR-2 [STATED] When `limit` is provided, `search()` shall return at most `limit` documents. (S3)  
- FR-3 [STATED] The documents returned when `limit` is used shall be ordered in the same order as they are stored in the database. (S3)  
- FR-4 [STATED] When `limit` is omitted, `search()` shall exhibit the same behaviour as the current implementation (i.e., return all matching documents). (S4)  
- FR-5 [STATED] The `limit` argument shall be applicable regardless of whether the search is performed on the default table or on a named table. (S5)  
- FR-6 [INFERRED] If `limit` is supplied with a non‑positive integer (zero or negative), `search()` would raise a `ValueError`. (S3, S4)  
- FR-7 [INFERRED] If `limit` is supplied with a non‑integer type, `search()` would raise a `TypeError`. (S3)

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=10)`, when the function is invoked, then the call succeeds without raising an exception and the returned object is a list (or iterable) of documents.  
- AC-2 (FR-2): Given a call `db.search(where('type') == 'log', limit=5)`, when the function returns, then the length of the result is ≤ 5.  
- AC-3 (FR-3): Given a database containing documents `[d1, d2, d3, d4, d5]` in storage order, when `db.search(where('type') == 'log', limit=3)` is executed, then the result is `[d1, d2, d3]`.  
- AC-4 (FR-4): Given a call `db.search(where('type') == 'log')` (no `limit` argument), when the function returns, then the result contains all matching documents, identical to the result of the current implementation.  
- AC-5 (FR-5): Given a named table `tbl` with documents, when `db.search(where('type') == 'log', limit=2, table='tbl')` is called, then the result contains at most 2 documents from `tbl` in storage order.  
- AC-6 (FR-6): Given a call `db.search(where('type') == 'log', limit=0)`, when the function is invoked, then a `ValueError` is raised with a message indicating that `limit` must be a positive integer.  
- AC-7 (FR-7): Given a call `db.search(where('type') == 'log', limit='ten')`, when the function is invoked, then a `TypeError` is raised indicating that `limit` must be an integer.

## Assumptions and open questions
- A-1 [ASSUMED] The existing `search()` API returns a list (or iterable) of document objects; the specification assumes this return type for testing. Impact if wrong: Acceptance criteria would need to be adjusted to match the actual return type (e.g., generator). Question: Does `search()` currently return a list, generator, or another collection type?  
- A-2 [ASSUMED] The phrase “in the order they are stored” refers to the natural insertion order of documents within the underlying storage engine. Impact if wrong: If the storage engine does not guarantee insertion order, the ordering requirement may need clarification or a different deterministic ordering (e.g., primary key). Question: Does the current implementation guarantee any ordering of results?  

## Non-goals
- Pagination or offset handling beyond the simple `limit` argument.  
- Performance optimizations for large limits; the specification only requires functional correctness.  
- Changes to the query language or additional filtering capabilities.

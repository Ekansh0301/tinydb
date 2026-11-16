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
- FR-5 [STATED] The `limit` argument shall be supported for searches on both the default table and any named table. (S5)  
- FR-6 [INFERRED] If `limit` is provided with a non‑positive integer (zero or negative), `search()` would raise a `ValueError`. (S3, S4)  
- FR-7 [INFERRED] If `limit` is provided with a non‑integer type, `search()`` would raise a `TypeError`. (S3)

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=10)`, when the function is invoked, then the call succeeds without raising an exception and the signature includes the `limit` parameter.
- AC-2 (FR-2): Given a database containing 25 matching documents, when `db.search(where('type') == 'log', limit=10)` is executed, then the returned collection contains exactly 10 documents.
- AC-3 (FR-3): Given a database where documents are stored in order D1, D2, D3, …, Dn, when `db.search(where('type') == 'log', limit=5)` is executed, then the returned documents are `[D1, D2, D3, D4, D5]`.
- AC-4 (FR-4): Given a call `db.search(where('type') == 'log')` (no `limit` argument), when the function is invoked, then the result set is identical to the result set of the current implementation (all matching documents, in the same order).
- AC-5 (FR-5): Given a named table `logs` with 12 matching rows, when `db.search(where('type') == 'log', limit=8, table='logs')` is executed, then the returned collection contains exactly 8 documents from that named table.
- AC-6 (FR-6): Given a call `db.search(where('type') == 'log', limit=0)`, when the function is invoked, then a `ValueError` is raised with a message indicating that `limit` must be a positive integer.
- AC-7 (FR-7): Given a call `db.search(where('type') == 'log', limit='ten')`, when the function is invoked, then a `TypeError` is raised indicating that `limit` must be an integer.

## Assumptions and open questions
- A-1 [ASSUMED] The existing `search()` API does not already accept a `limit` parameter under a different name (e.g., `max_results`). Impact if wrong: the change may be a duplicate or cause backward‑compatibility issues. Question: Does any current version of the library expose a similar pagination or limiting feature?
- A-2 [ASSUMED] The order “as they are stored” corresponds to the natural order of insertion or primary‑key order used by the current implementation. Impact if wrong: the returned ordering may differ from user expectations, requiring clarification of the ordering rule. Question: What exact ordering semantics does the current `search()` guarantee?

## Non-goals
- Implementing full pagination (offset/skip) beyond the simple `limit` functionality.
- Changing the underlying storage order or providing sorting capabilities.
- Supporting limit values larger than the total number of matching documents (the function will simply return all matches).

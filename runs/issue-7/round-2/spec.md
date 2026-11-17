# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S3: "Without `limit` nothing should change."
S4: "It should work on named tables too."

## Requirements
- FR-1 [ASSUMED] The `Table.search` method would accept an optional keyword argument `limit: int | None` (default `None`). When `limit` is provided and is a positive integer, the method would return at most `limit` documents that satisfy the query, preserving the order in which documents are stored in the table. (S2, S3, S4)
- FR-2 [STATED] The existing behaviour of `Table.search` shall remain unchanged when the `limit` argument is omitted or set to `None`. (S3)
- FR-3 [STATED] The `limit` argument shall be applicable to all tables, including the default table and any user‑named tables. (S4)

## Acceptance criteria
- AC-1 (FR-1): Given a table containing 20 documents where 15 match the condition `where('type') == 'log'`, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list shall contain exactly 10 documents, each of which satisfies the condition, and the documents shall appear in the same order as they are stored in the table.
- AC-2 (FR-1): Given a table containing 5 documents that all match the condition, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list shall contain all 5 matching documents (i.e., fewer than the limit) in storage order.
- AC-3 (FR-2): Given a table with any number of matching documents, when `db.search(where('type') == 'log')` is called (no `limit` argument), then the returned list shall contain all matching documents, identical to the current behaviour. 
- AC-4 (FR-3): Given a named table `logs` with 30 matching documents, when `db.table('logs').search(where('type') == 'log', limit=5)` is called, then the returned list shall contain exactly 5 documents from the `logs` table in storage order.

## Assumptions and open questions
- A-1 [ASSUMED] The `limit` parameter will be added as a keyword‑only argument to the existing `Table.search` signature without altering the positional arguments. Impact if wrong: If the API is changed to a positional argument or a different name, the acceptance criteria would need adjustment. Question: Should the limit be enforced after the cache lookup or should caching be aware of the limit value?
- A-2 [ASSUMED] The order of documents is defined by the internal storage order (i.e., the order of iteration over the table). Impact if wrong: If TinyDB defines a different deterministic order (e.g., sorted by `doc_id`), the "preserve order" clause may need clarification. Question: Does the current `Table.__iter__` guarantee insertion order across Python versions?

## Non-goals
- Changing the semantics of query caching beyond ensuring that a limited result set does not affect cached full result sets.
- Adding pagination metadata (e.g., total count) to the `search` response.
- Supporting complex limit expressions (e.g., negative numbers, zero) – such inputs are considered invalid and may raise a `ValueError`.

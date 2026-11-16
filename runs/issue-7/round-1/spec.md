# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."
S2: "`first_ten = db.search(where('type') == 'log')[:10]`"
S3: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S4: "Without `limit` nothing should change."
S5: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer. (S3)
- FR-2 [STATED] When `limit` is provided, `search()` shall return at most `limit` documents, ordered by their storage order. (S3)
- FR-3 [STATED] When `limit` is omitted, `search()` shall exhibit the same behaviour as the current implementation (i.e., return all matching documents). (S4)
- FR-4 [STATED] The `limit` argument shall be applicable regardless of whether the search is performed on the default table or on a named table. (S5)
- FR-5 [INFERRED] If `limit` is a non‑positive integer (zero or negative), `search()` would return an empty list. (S3, S4)
- FR-6 [INFERRED] If `limit` is larger than the total number of matching documents, `search()` would return all matching documents. (S3)

## Acceptance criteria
- AC-1 (FR-1): Given a call `db.search(where('type') == 'log', limit=10)`, when the function is invoked, then the call completes without raising an exception and the returned object is a list (or iterable) of documents.
- AC-2 (FR-2): Given a database containing 25 documents matching `where('type') == 'log'`, when `db.search(where('type') == 'log', limit=10)` is executed, then the returned collection contains exactly 10 documents, and the documents appear in the same order as they are stored in the table.
- AC-3 (FR-3): Given a database containing 15 documents matching `where('type') == 'log'`, when `db.search(where('type') == 'log')` is executed (no `limit` argument), then the returned collection contains exactly 15 documents, matching the current behaviour of `search()`.
- AC-4 (FR-4): Given a named table `logs` with 8 matching documents, when `db.search(where('type') == 'log', limit=5, table='logs')` is executed, then the returned collection contains exactly 5 documents from that named table, ordered as stored.
- AC-5 (FR-5): Given any database state, when `db.search(where('type') == 'log', limit=0)` is executed, then the returned collection is empty.
- AC-6 (FR-5): Given any database state, when `db.search(where('type') == 'log', limit=-3)` is executed, then the returned collection is empty.
- AC-7 (FR-6): Given a database containing 4 matching documents, when `db.search(where('type') == 'log', limit=10)` is executed, then the returned collection contains exactly 4 documents (i.e., all matches).

## Assumptions and open questions
- A-1 [ASSUMED] The term “order they are stored” refers to the natural insertion order of documents within the underlying storage engine. Impact if wrong: If the storage engine defines a different default ordering (e.g., primary‑key order), the returned sequence may not match UI expectations. Question: Does the current `search()` guarantee any specific ordering, and should `limit` preserve that ordering?
- A-2 [ASSUMED] The `search()` API already supports a `table` parameter for named tables; the new `limit` argument will be added alongside it without altering existing signatures. Impact if wrong: If `search()` does not currently accept a `table` argument, the implementation may need to expose a separate overload or keyword, affecting backward compatibility.

## Non-goals
- Pagination mechanisms beyond a simple `limit` (e.g., offset, cursor‑based paging).
- Performance optimizations for large limits; the requirement only specifies functional behaviour.
- Changing the default ordering of results; the specification assumes the existing ordering is retained.

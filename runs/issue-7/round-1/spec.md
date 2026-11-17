# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything: `first_ten = db.search(where('type') == 'log')[:10]`"
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S3: "Without `limit` nothing should change."
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` function shall accept an optional keyword argument `limit` of type integer (S2).
- FR-2 [STATED] When `limit` is provided, `search()` shall return at most `limit` documents, preserving the order in which documents are stored in the table (S2).
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as it does today, returning all matching documents (S3).
- FR-4 [STATED] The `limit` argument shall be applicable when `search()` is invoked on any table, including named tables (S4).

## Acceptance criteria
- AC-1 (FR-1 & FR-2): Given a table with 100 matching documents, when `db.search(where('type') == 'log', limit=10)` is called, then the returned list length shall be 10 and the items shall be the first 10 documents according to the table’s storage order.
- AC-2 (FR-3): Given a table with 15 matching documents, when `db.search(where('type') == 'log')` is called (no `limit` argument), then the returned list length shall be 15 and the list shall contain the same documents in the same order as the current implementation without `limit`.
- AC-3 (FR-4): Given a named table `logs` with 20 matching documents, when `db.search(where('type') == 'log', limit=5, table='logs')` is called, then the returned list length shall be 5 and the items shall be the first 5 documents of the `logs` table in storage order.
- AC-4 (FR-4, error handling): Given a call `db.search(where('type') == 'log', limit=-1)`, when the function is executed, then a `ValueError` shall be raised with a message indicating that `limit` must be a positive integer.

## Assumptions and open questions
- A-1 [ASSUMED] The “order they are stored” is a deterministic order defined by the underlying storage engine (e.g., insertion order). Impact if wrong: If the storage order is not deterministic, the returned subset may vary between calls, breaking UI expectations. Question: How is storage order defined for each table type, and does it remain stable across restarts?
- A-2 [ASSUMED] The existing `search()` signature allows additional keyword arguments without breaking backward compatibility. Impact if wrong: Adding `limit` could cause signature conflicts with user‑defined extensions. Question: Are there any existing extensions that already use a `limit` keyword?

## Non-goals
- Implementing pagination or offset handling; only a simple `limit` is required.
- Changing the default ordering of results; the specification preserves existing order.
- Providing server‑side query optimization beyond limiting the result set size.


## Stopped
Stage 1 could not pass its check: requirements without an acceptance criterion: FR-2

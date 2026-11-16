# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything:"  
S2: "`first_ten = db.search(where('type') == 'log')[:10]`"  
S3: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"  
S4: "Without `limit` nothing should change."  
S5: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The system shall allow the `search()` function to accept an optional keyword argument `limit` (integer) that restricts the number of returned documents to at most the supplied value, preserving the storage order of the matches. (S3)  
- FR-2 [STATED] The system shall preserve the current behaviour of `search()` when the `limit` argument is omitted; i.e., all matching documents are returned. (S4)  
- FR-3 [STATED] The system shall apply the `limit` behaviour consistently for searches on named tables as well as the default table. (S5)  
- FR-4 [INFERRED] The system would raise a `ValueError` if a negative integer is supplied for `limit`. (S3)  
- FR-5 [ASSUMED] The system would treat non‑integer values for `limit` as a type error, raising `TypeError`. Impact if wrong: callers might receive unexpected results or uncaught exceptions. Question: Should the API coerce numeric types (e.g., floats) to int or reject them?

## Acceptance criteria
- AC-1 (FR-1): Given a database containing 25 documents that satisfy `where('type') == 'log'`, when `db.search(where('type') == 'log', limit=10)` is executed, then the returned list contains exactly 10 documents and the documents appear in the same order as they are stored in the database.  
- AC-2 (FR-2): Given the same database state, when `db.search(where('type') == 'log')` is executed without a `limit` argument, then the returned list contains all 25 matching documents in storage order.  
- AC-3 (FR-3): Given a named table `logs` containing 8 matching documents, when `db.search(where('type') == 'log', limit=5, table='logs')` is executed, then the returned list contains exactly 5 documents in storage order from that table.  
- AC-4 (FR-4): Given any database, when `db.search(where('type') == 'log', limit=-3)` is executed, then a `ValueError` is raised with a message indicating that `limit` must be non‑negative.  
- AC-5 (FR-5): Given any database, when `db.search(where('type') == 'log', limit='ten')` is executed, then a `TypeError` is raised indicating that `limit` must be an integer.

## Assumptions and open questions
- A-1 [ASSUMED] The `limit` argument is expected to be an integer. Impact if wrong: If callers pass other numeric types (e.g., float) the API may need to define conversion or error handling. Question: Should the API silently truncate floats to int, or reject them with `TypeError`?  
- A-2 [ASSUMED] The storage order of documents is deterministic and defined by the underlying database engine. Impact if wrong: If order is not guaranteed, the “first N” semantics could be ambiguous, affecting UI expectations. Question: Is there an existing ordering guarantee for `search()` results that must be documented?

## Non-goals
- Changing the underlying query language or adding pagination metadata beyond the simple `limit` argument.  
- Implementing sorting or offset functionality; only the `limit` parameter is addressed.  
- Modifying the behavior of `search()` for remote or distributed back‑ends beyond the current single‑process implementation.

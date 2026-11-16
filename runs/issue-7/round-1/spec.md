# Spec
## Source statements
S1: "When I show results in a UI I only need the first few matches, but `search()` always returns everything."
S2: "Could `search()` take an optional `limit` argument so that `db.search(where('type') == 'log', limit=10)` returns at most 10 documents, in the order they are stored?"
S3: "Without `limit` nothing should change."
S4: "It should work on named tables too."

## Requirements
- FR-1 [STATED] The `search()` method shall accept an optional keyword argument `limit` of type `int` (S2).  
- FR-2 [STATED] When `limit` is provided, `search()` shall return at most `limit` documents, preserving the order in which the documents are stored in the table (S2).  
- FR-3 [STATED] When `limit` is omitted, `search()` shall behave exactly as the current implementation, returning all matching documents (S3).  
- FR-4 [STATED] The `limit` argument shall be supported for all tables, including named tables (S4).  
- FR-5 [INFERRED] If `limit` is a non‑positive integer (zero or negative), `search()` shall return an empty list (inferred from typical limit semantics).  
- FR-6 [INFERRED] If `limit` is greater than the number of matching documents, `search()` shall return all matching documents (inferred from “at most `limit`”).  

## Acceptance criteria
- AC-1 (FR-1): Given a table with any documents, when calling `db.search(where('type') == 'log', limit=5)`, then the call completes without raising an exception and the returned value is a list.
- AC-2 (FR-2): Given a table containing 20 documents that satisfy `where('type') == 'log'`, when calling `db.search(where('type') == 'log', limit=10)`, then the returned list length is exactly 10 and the documents appear in the same order as they are stored in the table.
- AC-3 (FR-3): Given a table containing 15 matching documents, when calling `db.search(where('type') == 'log')` (no limit argument), then the returned list length is 15 and the list is identical to the list returned by the current implementation without the new argument.
- AC-4 (FR-4): Given a named table `db.table('archive')` with 8 matching documents, when calling `db.table('archive').search(where('type') == 'log', limit=3)`, then the returned list length is 3 and the documents are in storage order.
- AC-5 (FR-5): Given any table, when calling `db.search(where('type') == 'log', limit=0)`, then the returned list is empty (`[]`).  
- AC-6 (FR-5): Given any table, when calling `db.search(where('type') == 'log', limit=-5)`, then the returned list is empty (`[]`).  
- AC-7 (FR-6): Given a table with 4 matching documents, when calling `db.search(where('type') == 'log', limit=10)`, then the returned list length is 4 and the list matches the full set of matching documents.

## Assumptions and open questions
- A-1 [ASSUMED] The order of documents “as they are stored” corresponds to the order returned by the existing `search()` implementation (i.e., insertion order). Impact if wrong: The new `limit` behavior could return documents in an unexpected order, causing UI inconsistencies. Question: Does TinyDB guarantee a stable order for `search()` results across versions?
- A-2 [ASSUMED] The `limit` argument will be passed as a keyword argument only; positional usage is not required. Impact if wrong: Users attempting `db.search(cond, 10)` would receive a TypeError. Question: Should positional `limit` be supported for backward compatibility?
- A-3 [ASSUMED] Adding the `limit` parameter will not affect the public API of other overloads (e.g., `search(regex, flags)`) because they are in a different module. Impact if wrong: Name collisions could cause runtime errors. Question: Are there any existing `search` signatures that already accept a second positional argument that could conflict?

## Non-goals
- Implementing pagination or offset functionality beyond the simple `limit` parameter.  
- Changing the underlying storage engine or indexing strategy to improve performance of limited queries.  
- Providing a streaming interface for very large result sets.  
- Supporting limit semantics on non‑table objects (e.g., queries on the database object itself).

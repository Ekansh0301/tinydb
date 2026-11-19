# Spec
## Source statements
S1: "remove() deleted the wrong thing ... I called remove with a query and a list of ids at the same time ... a document that has nothing to do with my query is gone. Same with update, it changed a document I didn't expect."
## Requirements
- FR-1 [STATED] The `Table.remove` method shall, when both a query (`cond`) and a list of document IDs (`doc_ids`) are provided, delete only the documents that satisfy **both** the query and are among the specified IDs. (S1)
- FR-2 [STATED] The `Table.remove` method shall return a list of the IDs that were actually removed. (S1)
- FR-3 [INFERRED] The existing behaviour of `remove` when only `doc_ids` is given (remove those IDs if they exist) must remain unchanged.
- FR-4 [INFERRED] The existing behaviour of `remove` when only `cond` is given (remove all matching documents) must remain unchanged.
## Acceptance criteria
- AC-1 (FR-1, FR-2): Given a table with several documents, when `remove(cond=query, doc_ids=[list])` is called, then only documents whose IDs are in the list **and** match the query are removed, and the returned list contains exactly those IDs.
- AC-2 (FR-3): Given a table with documents, when `remove(doc_ids=[ids])` is called (no query), then only the specified existing IDs are removed and the returned list contains those IDs.
- AC-3 (FR-4): Given a table with documents, when `remove(cond=query)` is called (no doc_ids), then all documents matching the query are removed and the returned list contains their IDs.
## Assumptions and open questions
- A-1 [ASSUMED] The `Table.update` method has similar combined‑parameter semantics; however the issue only mentions `remove`, so we address only `remove`. Impact if wrong: update may still have unexpected behaviour but not covered by tests.
## Non-goals
- Changing the behaviour of `update`.
- Introducing new public APIs.
